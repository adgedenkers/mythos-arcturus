#!/bin/bash
set -e

# ============================================================================
# Downloads Triage — One-Time Cleanup
# ============================================================================
# Organizes ~/Downloads into archived categories so the docs-librarian
# system can take over on a clean slate.
#
# This does NOT auto-import into /opt/mythos/docs — that's the librarian's
# job. This just sorts the Downloads junkyard into labeled bins.
#
# Nothing is deleted. Everything is moved to ~/Downloads/_archived/<category>
# ============================================================================

DL="$HOME/Downloads"
A="$DL/_archived"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== Downloads Triage — $TIMESTAMP ==="
echo ""

# Safety: snapshot
find "$DL" -maxdepth 1 -type f | sort > "/tmp/downloads_before_${TIMESTAMP}.txt"
echo "Manifest saved: /tmp/downloads_before_${TIMESTAMP}.txt"
echo ""

# Create bins
for bin in patches sessions handoffs scripts schemas deliverables \
           images tarot seraphe iris_bench build_artifacts \
           docs_candidates duplicates misc; do
    mkdir -p "$A/$bin"
done

# Helper
archive() {
    local file="$1"
    local bin="$2"
    [ -f "$DL/$file" ] && mv -v "$DL/$file" "$A/$bin/" || true
}

archive_dir() {
    local dir="$1"
    local bin="$2"
    [ -d "$DL/$dir" ] && mv -v "$DL/$dir" "$A/$bin/" || true
}

# -------------------------------------------------------------------------
# Consumed patches (directories and zips)
# -------------------------------------------------------------------------
echo "[Patches — consumed build artifacts]"
for d in NEU-0002_perception_integration \
         NEU-0003_perception_router_schema_fix \
         NEU-0004_perception_hook_fix \
         NEU-0006_idle_task_engine_fix \
         docs-cleanup-kit docs_update seraphe-lunar-tool; do
    archive_dir "$d" "patches"
done

for f in "NEU-0006_idle_task_engine_fix(1).zip" \
         "LOG-0015_archaeology_round1.zip" \
         "SYS-0022_backfill_balances.zip" \
         "SYS-0033_benchmark_round2.zip" \
         "SYS-DRAFT_fix_transaction_hash.zip" \
         "docs-cleanup-kit.zip" \
         "docs_update.zip" \
         "seraphe-lunar-tool.zip" \
         "iris_resonance_bench.zip"; do
    archive "$f" "patches"
done
archive_dir "iris_resonance_bench" "patches"
echo ""

# -------------------------------------------------------------------------
# Session JSONs
# -------------------------------------------------------------------------
echo "[Sessions — session summaries and exports]"
for f in "$DL"/session_*.json "$DL"/conversation_summary_*.json \
         "$DL"/mythos_session_summary.json "$DL"/session_build_summary.json \
         "$DL"/NEU-0008_session_summary.json; do
    [ -f "$f" ] && mv -v "$f" "$A/sessions/" || true
done
echo ""

# -------------------------------------------------------------------------
# Handoffs
# -------------------------------------------------------------------------
echo "[Handoffs — session handoff docs]"
for f in HANDOFF.md handoff_phase4_phase3.md NEU-0009_0010_HANDOFF.md \
         SELF_HEALING_HANDOFF.md iris_voice_tuning_handoff.md \
         sdip_chunks_handoff.md Mythos_Build_Log_March_7-8_2026.md \
         IRIS_SEED_DATASET_HANDOFF_PROMPT.md IRIS_SOURCE_MATERIAL_GENERATOR_PROMPT.md; do
    archive "$f" "handoffs"
done
echo ""

# -------------------------------------------------------------------------
# Python scripts (build tools, one-off utilities)
# -------------------------------------------------------------------------
echo "[Scripts — Python utilities and build tools]"
for f in apply_docs_update.py cleanup_old_models.py daily_task_planner.py \
         ephemeris.py financial_overview.py fix_confab_carveout.py \
         idea_backlog_manager.py ollama_builder.py ollama_grinder.py \
         patch_nothink.py person_deep_dive.py person_research.py \
         reimport_account.py search_documents.py seraphe_lunar_transits.py \
         spending_analysis.py update_architecture.py update_docs_20260311.py \
         vault_sorter.py; do
    archive "$f" "scripts"
done
echo ""

# -------------------------------------------------------------------------
# JSON skill schemas and build plans
# -------------------------------------------------------------------------
echo "[Schemas — JSON skill schemas and build plans]"
for f in "$DL"/*_build_plan*.json "$DL"/add_idea.json "$DL"/bench_config_fixed.json \
         "$DL"/build_plan.json "$DL"/complete_routine.json "$DL"/daily_briefing.json \
         "$DL"/daily_task_planner.json "$DL"/extract_date_range.json \
         "$DL"/extract_search_terms.json "$DL"/format_financial_summary.json \
         "$DL"/format_person_summary.json "$DL"/idea_backlog_manager.json \
         "$DL"/log_checkin.json "$DL"/log_life_event.json \
         "$DL"/neo4j_graph_search.json "$DL"/query_bills_due.json \
         "$DL"/query_calendar.json "$DL"/query_natal_chart.json \
         "$DL"/query_routines.json "$DL"/query_shopping_lists.json \
         "$DL"/query_transactions.json "$DL"/rank_by_recency.json \
         "$DL"/rank_by_relevance.json "$DL"/spending_analysis.json; do
    [ -f "$f" ] && mv -v "$f" "$A/schemas/" || true
done
echo ""

# -------------------------------------------------------------------------
# Tarot session exports
# -------------------------------------------------------------------------
echo "[Tarot — session exports and references]"
for f in "$DL"/tarot_20260*.json "$DL"/tarot_20260*_index.md; do
    [ -f "$f" ] && mv -v "$f" "$A/tarot/" || true
done
echo ""

# -------------------------------------------------------------------------
# Seraphe deliverables (xlsx, jsx, pdf)
# -------------------------------------------------------------------------
echo "[Seraphe — deliverables and data exports]"
for f in "$DL"/seraphe_*.xlsx "$DL"/seraphe_*.jsx "$DL"/seraphe_*.pdf \
         "$DL"/seraphe_lunar_2026_03.json "$DL"/seraphe_lunar_2026_03.txt; do
    [ -f "$f" ] && mv -v "$f" "$A/seraphe/" || true
done
echo ""

# -------------------------------------------------------------------------
# Images
# -------------------------------------------------------------------------
echo "[Images — ChatGPT generations, backgrounds, jpegs]"
for f in "$DL"/ChatGPT\ Image*.png "$DL"/triangles-background-with-footer.jpeg \
         "$DL"/hex-background; do
    [ -f "$f" ] && mv -v "$f" "$A/images/" || true
done
for f in "$DL"/jpeg "$DL"/jpeg\(1\) "$DL"/jpeg\(2\) "$DL"/jpeg\(3\); do
    [ -f "$f" ] && mv -v "$f" "$A/images/" || true
done
echo ""

# -------------------------------------------------------------------------
# Duplicates (numbered copies)
# -------------------------------------------------------------------------
echo "[Duplicates — numbered copies of files]"
for f in "$DL"/COMMAND_CENTER\(1\).md "$DL"/COMMAND_CENTER\(2\).md \
         "$DL"/distributed_cognitive_graph_summary\(1\).md \
         "$DL"/gosling_analysis\(1\).md \
         "$DL"/our_money_our_system\(1\).docx "$DL"/our_money_our_system\(2\).docx \
         "$DL"/our_money_our_system\(3\).docx "$DL"/our_money_our_system\(4\).docx \
         "$DL"/SEED_SOURCE_01_IDENTITY_IRIS\(1\).md "$DL"/SEED_SOURCE_01_IDENTITY_IRIS\(2\).md \
         "$DL"/iris_sovereign_dataset\(1\).json \
         "$DL"/transit_pressure_map\(1\).jsx "$DL"/transit_pressure_map\(2\).jsx \
         "$DL"/transit_pressure_map\(3\).jsx \
         "$DL"/transit_pressure_map_seraphe\(1\).jsx \
         "$DL"/seraphe_calendar_2026\(1\).jsx "$DL"/seraphe_calendar_2026\(2\).jsx \
         "$DL"/seraphe_lunar_calendar_march2026-alt.jsx \
         "$DL"/seraphe_lineage_print\(1\).xlsx \
         "$DL"/memory_search_composite_build_plan\(1\).json \
         "$DL"/memory_search_composite_build_plan\(2\).json \
         "$DL"/session_reference_2026-03-10\(1\).json \
         "$DL"/cognitive_ai_architecture_master_list.md \
         "$DL"/cognitive_ai_architecture_supplement.md \
         "$DL"/sahiran_the_turning\(1\).md; do
    [ -f "$f" ] && mv -v "$f" "$A/duplicates/" || true
done
# Numbered narrow-ruled-paper PDFs
for f in "$DL"/narrow-ruled-paper\ \(*.pdf "$DL"/narrow-ruled-paper.pdf.zip; do
    [ -f "$f" ] && mv -v "$f" "$A/duplicates/" || true
done
echo ""

# -------------------------------------------------------------------------
# Build artifacts (SQL, cypher, misc one-offs)
# -------------------------------------------------------------------------
echo "[Build artifacts — SQL, cypher, data files]"
for f in fix_bills.sql family_tree_graph_update.cypher \
         family_tree_supplemental.cypher family_tree_update_final.cypher \
         system_archaeology.yaml usaa-archive-20250101.csv \
         sunmark-archive-20250101.CSV google-chrome-stable_current_amd64.deb; do
    archive "$f" "build_artifacts"
done
# Family data xlsx files
for f in "$DL"/family_*.xlsx "$DL"/denkers_family_complete.xlsx; do
    [ -f "$f" ] && mv -v "$f" "$A/build_artifacts/" || true
done
echo ""

# -------------------------------------------------------------------------
# Iris-specific deliverables
# -------------------------------------------------------------------------
echo "[Iris — seed datasets, sovereign datasets, decision tool]"
for f in iris_sovereign_dataset.json iris-decide sovereign-align-test \
         SEED_SOURCE_01_IDENTITY_IRIS.md; do
    archive "$f" "iris_bench"
done
echo ""

# -------------------------------------------------------------------------
# Docs candidates — markdown files that SHOULD go to /opt/mythos/docs
# These stay in _archived/docs_candidates for the librarian to process
# once frontmatter is added
# -------------------------------------------------------------------------
echo "[Docs candidates — markdown for future librarian import]"
for f in AUTONOMIC_SYSTEM.md CC3_ARCHITECTURE.md COMMAND_CENTER.md \
         cognitive_ai_architecture_master_list_25.md \
         distributed_cognitive_graph_summary.md \
         gosling_analysis.md iris_evolution_blueprint.md \
         IRIS_MEMORY_CONSOLIDATION_PIPELINE.md IRIS_TEST_TOOL.md \
         moon_cheatsheet.md morse-code-reference.md braille-reference.md \
         numerology_fractal_system_spec.md \
         numerology_tarot_fractals_framework_expanded.md \
         numerology_tarot_fractals_framework.md \
         "Mythos CLI Tools.md" mythos-chatgpt-prompt.md \
         "mythos-chatgpt-prompt(1).md" \
         sahiran_the_turning.md sdip_reference.md \
         seraphe_natal_lunar_points.md synastry_seraphe_brandi.md \
         tarot_complete_78_card_reference.md \
         tarot_complete_structured_reference.md \
         tarot_major_minor_arcana_summary.md \
         vault_operations_guide.md astrology_for_dummies.md; do
    archive "$f" "docs_candidates"
done
echo ""

# -------------------------------------------------------------------------
# Remaining deliverables (docx, jsx, pdf, py that are output files)
# -------------------------------------------------------------------------
echo "[Deliverables — final output files]"
for f in "$DL"/our_money_our_system.docx "$DL"/financial_sovereignty_plan.docx \
         "$DL"/iris_cognitive_architecture_v1.docx \
         "$DL"/narrow-ruled-paper.pdf \
         "$DL"/planetary_harmonic_field_map.jsx \
         "$DL"/SDIPDashboard.jsx \
         "$DL"/seraphe_calendar_2026.jsx \
         "$DL"/seraphe_lunar_calendar_march2026.jsx \
         "$DL"/transit_pressure_map.jsx \
         "$DL"/transit_pressure_map_seraphe.jsx; do
    [ -f "$f" ] && mv -v "$f" "$A/deliverables/" || true
done
echo ""

# -------------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------------
echo "============================================"
echo "  Triage complete."
echo ""
echo "  Archived to: $A/"
echo ""
REMAINING=$(find "$DL" -maxdepth 1 -type f 2>/dev/null | wc -l)
echo "  Files remaining in ~/Downloads: $REMAINING"
if [ "$REMAINING" -gt 0 ]; then
    echo ""
    echo "  Remaining files:"
    find "$DL" -maxdepth 1 -type f -printf "    %f\n" | sort
fi
echo ""
echo "  Next step: Add frontmatter to docs_candidates/"
echo "  Then: docs-librarian scan ~/Downloads/_archived/docs_candidates"
echo "============================================"
