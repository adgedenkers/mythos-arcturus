#!/usr/bin/env bash
# =============================================================================
# Mythos Doc Watcher — inotify-based auto-commit daemon
# Patch 0174 — Foundation layer for live telemetry transport
#
# Monitors key documentation files and the docs/live/ directory.
# When changes are detected, waits for writes to settle (debounce),
# then auto-commits and pushes to GitHub.
# =============================================================================

set -euo pipefail

# --- Configuration ---
MYTHOS_ROOT="/opt/mythos"
DOCS_DIR="${MYTHOS_ROOT}/docs"
LIVE_DIR="${DOCS_DIR}/live"
LOG_FILE="/var/log/mythos/doc-watcher.log"
DEBOUNCE_SECONDS=45          # Wait for writes to settle
COOLDOWN_SECONDS=120         # Min seconds between pushes
MAX_LOG_SIZE_MB=10           # Rotate log if it exceeds this

# Files/dirs to watch (space-separated for inotifywait)
WATCH_PATHS=(
    "${DOCS_DIR}/TODO.md"
    "${DOCS_DIR}/ARCHITECTURE.md"
    "${LIVE_DIR}"
)

# --- Ensure log directory exists ---
mkdir -p "$(dirname "$LOG_FILE")"

# --- Logging ---
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

# --- Log rotation (simple) ---
rotate_log_if_needed() {
    if [[ -f "$LOG_FILE" ]]; then
        local size_mb
        size_mb=$(du -m "$LOG_FILE" 2>/dev/null | cut -f1)
        if [[ "$size_mb" -ge "$MAX_LOG_SIZE_MB" ]]; then
            mv "$LOG_FILE" "${LOG_FILE}.1"
            log "Log rotated (was ${size_mb}MB)"
        fi
    fi
}

# --- Validate watch paths exist ---
validate_paths() {
    local valid_paths=()
    for path in "${WATCH_PATHS[@]}"; do
        if [[ -e "$path" ]]; then
            valid_paths+=("$path")
        else
            log "WARN: Watch path does not exist yet: $path (will be picked up on restart)"
        fi
    done

    if [[ ${#valid_paths[@]} -eq 0 ]]; then
        log_error "No valid watch paths found. Exiting."
        exit 1
    fi

    WATCH_PATHS=("${valid_paths[@]}")
}

# --- Git operations ---
git_commit_and_push() {
    cd "$MYTHOS_ROOT" || { log_error "Cannot cd to $MYTHOS_ROOT"; return 1; }

    # Stage only docs
    git add docs/ 2>/dev/null || true

    # Check if there's actually anything to commit
    if git diff --cached --quiet 2>/dev/null; then
        log "No staged changes — skipping commit"
        return 0
    fi

    # Build commit message from changed files
    local changed_files
    changed_files=$(git diff --cached --name-only 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
    local commit_msg="[doc-watcher] auto-sync: ${changed_files}"

    if git commit -m "$commit_msg" 2>>"$LOG_FILE"; then
        log "Committed: $commit_msg"
    else
        log_error "Commit failed"
        return 1
    fi

    # Push (with retry)
    local retries=3
    for ((i=1; i<=retries; i++)); do
        if git push origin main 2>>"$LOG_FILE"; then
            log "Pushed to origin/main"
            return 0
        else
            log "Push attempt $i/$retries failed, waiting 10s..."
            sleep 10
        fi
    done

    log_error "Push failed after $retries attempts"
    return 1
}

# --- Main loop ---
main() {
    log "========================================="
    log "Mythos Doc Watcher starting"
    log "Watching: ${WATCH_PATHS[*]}"
    log "Debounce: ${DEBOUNCE_SECONDS}s | Cooldown: ${COOLDOWN_SECONDS}s"
    log "========================================="

    # Check dependencies
    if ! command -v inotifywait &>/dev/null; then
        log_error "inotifywait not found. Install: sudo apt install inotify-tools"
        exit 1
    fi

    validate_paths

    local last_push=0

    while true; do
        rotate_log_if_needed

        # Block until a change is detected
        # Watch for: create, modify, delete, move, close_write
        inotifywait -q -r \
            -e close_write \
            -e create \
            -e delete \
            -e moved_to \
            "${WATCH_PATHS[@]}" 2>/dev/null || {
                log "inotifywait exited unexpectedly, restarting in 5s..."
                sleep 5
                continue
            }

        log "Change detected — debouncing ${DEBOUNCE_SECONDS}s..."

        # Debounce: keep waiting while changes continue
        local debounce_end=$(($(date +%s) + DEBOUNCE_SECONDS))
        while true; do
            local remaining=$((debounce_end - $(date +%s)))
            if [[ $remaining -le 0 ]]; then
                break
            fi
            # Wait for more changes with timeout = remaining debounce time
            if inotifywait -q -r -t "$remaining" \
                -e close_write \
                -e create \
                -e delete \
                -e moved_to \
                "${WATCH_PATHS[@]}" 2>/dev/null; then
                # More changes — reset debounce window
                debounce_end=$(($(date +%s) + DEBOUNCE_SECONDS))
                log "  Additional changes — debounce reset"
            fi
            # If inotifywait timed out (no more changes), loop exits naturally
        done

        log "Debounce complete — checking cooldown..."

        # Cooldown check
        local now
        now=$(date +%s)
        local elapsed=$((now - last_push))
        if [[ $elapsed -lt $COOLDOWN_SECONDS ]]; then
            local wait_time=$((COOLDOWN_SECONDS - elapsed))
            log "Cooldown active — waiting ${wait_time}s more"
            sleep "$wait_time"
        fi

        # Do the commit + push
        log "Committing and pushing..."
        if git_commit_and_push; then
            last_push=$(date +%s)
            log "Sync complete ✓"
        else
            log_error "Sync failed — will retry on next change"
        fi
    done
}

# --- Signal handling ---
trap 'log "Doc Watcher shutting down (signal received)"; exit 0' SIGTERM SIGINT SIGHUP

main "$@"
