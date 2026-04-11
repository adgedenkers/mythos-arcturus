#!/usr/bin/env python3
"""
RØDE Wireless GO — File Transfer with Dedup
Auto-identifies transmitters by USB serial number from /dev/disk/by-id/
No flags needed — plug in and run.
First time a new serial is seen, you name it once. Saved to:
  ~/.config/rode-transfer/devices.json
Deduplication via quick fingerprint manifest at destination.
Fingerprint = MD5(file_size + first_64KB + last_64KB) — reads <128KB per file
regardless of recording length. Files already imported are skipped automatically.
Device files are NEVER deleted — firmware handles its own storage reclamation.
Files are sorted into year/month folders by RECORDING DATE, not import date.
Usage:
  rode-transfer                        # fully automatic (interactive prompts)
  rode-transfer --yes                  # zero prompts (for udev/automation)
  rode-transfer --dest /opt/mythos/voice_memos/incoming
  rode-transfer --dry-run              # preview only
  rode-transfer --list-devices         # show known devices
  rode-transfer --forget SERIAL        # remove a saved device name
"""
import os, sys, json, hashlib, argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (Progress, BarColumn, TextColumn,
                           TimeRemainingColumn, FileSizeColumn, TransferSpeedColumn)
from rich.prompt import Prompt, Confirm
from rich import box
from rich.align import Align
from rich.rule import Rule
console = Console()
AUDIO_EXTENSIONS = {
    '.wav', '.WAV', '.mp3', '.MP3', '.m4a', '.M4A',
    '.aac', '.AAC', '.flac', '.FLAC', '.ogg', '.OGG',
}
CHUNK_SIZE     = 65536  # 64KB — used for fingerprint and copy buffer
CONFIG_PATH    = Path.home() / '.config' / 'rode-transfer' / 'devices.json'
BY_ID_DIR      = Path('/dev/disk/by-id')
RODE_PREFIX    = 'usb-RODE_Wireless_GO_'
MANIFEST_NAME  = '.rode-manifest.json'
DEFAULT_DEST   = Path('/opt/mythos/voice_memos/incoming')
BANNER = """\
[bold cyan]██████╗  ██████╗ ██████╗ ███████╗[/bold cyan]
[bold cyan]██╔══██╗██╔═══██╗██╔══██╗██╔════╝[/bold cyan]
[bold cyan]██████╔╝██║   ██║██║  ██║█████╗  [/bold cyan]
[bold cyan]██╔══██╗██║   ██║██║  ██║██╔══╝  [/bold cyan]
[bold cyan]██║  ██║╚██████╔╝██████╔╝███████╗[/bold cyan]
[bold cyan]╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝[/bold cyan]
[dim]Wireless GO · Dual-Mic Transfer · Dedup v4[/dim]"""
MIC_STYLES = ['bold cyan', 'bold magenta', 'bold green', 'bold yellow']
# ── Quick fingerprint ─────────────────────────────────────────────────────────
def quick_fingerprint(filepath: Path, file_size: int) -> str:
    """
    Fast dedup fingerprint: MD5 of (file_size + first 64KB + last 64KB).
    Reads at most 128KB regardless of file size. For audio files this is
    collision-safe — two different recordings won't share identical size
    AND identical first/last chunks.
    """
    h = hashlib.md5()
    h.update(str(file_size).encode())
    with open(filepath, 'rb') as f:
        head = f.read(CHUNK_SIZE)
        h.update(head)
        if file_size > CHUNK_SIZE:
            f.seek(-CHUNK_SIZE, 2)
            h.update(f.read(CHUNK_SIZE))
    return h.hexdigest()
# ── Config ────────────────────────────────────────────────────────────────────
def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    return {}
def save_config(cfg: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
# ── Month folder helper ───────────────────────────────────────────────────────
def month_subdir(dt: datetime) -> str:
    """Return 'YYYY/MM-MonthName' subdir based on recording date."""
    return f"{dt.strftime('%Y')}/{dt.strftime('%m-%B')}"
# ── Manifest ──────────────────────────────────────────────────────────────────
class Manifest:
    """Tracks every file ever imported by quick fingerprint."""
    def __init__(self, base_dir: Path):
        self.path = base_dir / MANIFEST_NAME
        self.data = self._load()
    def _load(self) -> dict:
        if self.path.exists():
            try:
                with open(self.path) as f:
                    d = json.load(f)
                if d.get("version", 1) < 2:
                    d = self._migrate_v1_to_v2(d)
                return d
            except (json.JSONDecodeError, IOError):
                return {"version": 2, "files": {}}
        return {"version": 2, "files": {}}
    def _migrate_v1_to_v2(self, old: dict) -> dict:
        console.print("[yellow]Migrating manifest v1 → v2 (one-time re-fingerprint)...[/yellow]")
        dest_dir = self.path.parent
        new_files = {}
        migrated = 0
        dropped = 0
        for old_hash, info in old.get("files", {}).items():
            fname = info.get("file", "")
            fpath = dest_dir / fname
            if fpath.exists():
                try:
                    size = fpath.stat().st_size
                    fp = quick_fingerprint(fpath, size)
                    new_files[fp] = info
                    migrated += 1
                except OSError:
                    dropped += 1
            else:
                dropped += 1
        console.print(f"  [green]Migrated {migrated} entries, dropped {dropped} stale[/green]")
        return {"version": 2, "files": new_files}
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix('.tmp')
        with open(tmp, 'w') as f:
            json.dump(self.data, f, indent=2)
        tmp.rename(self.path)
    @property
    def files(self) -> dict:
        return self.data.setdefault("files", {})
    def has_fingerprint(self, fp: str) -> bool:
        return fp in self.files
    def record(self, fp: str, filename: str, size: int, mic: str):
        self.files[fp] = {
            "file": filename,
            "size": size,
            "mic": mic,
            "imported_at": datetime.now().isoformat(),
        }
    @property
    def count(self) -> int:
        return len(self.files)
# ── Device model ──────────────────────────────────────────────────────────────
@dataclass
class RodeDevice:
    serial:      str
    mount_point: Optional[Path]
    name:        str
    by_id_path:  Path
def _find_mount(dev_node: Path) -> Optional[Path]:
    try:
        with open('/proc/mounts') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and parts[0] == str(dev_node):
                    return Path(parts[1])
    except OSError:
        pass
    return None
def find_rode_devices() -> list:
    if not BY_ID_DIR.exists():
        return []
    devices = []
    for entry in sorted(BY_ID_DIR.iterdir()):
        name = entry.name
        if not name.startswith(RODE_PREFIX) or 'part' in name:
            continue
        suffix = name[len(RODE_PREFIX):]
        serial = suffix.rsplit('-', 1)[0]
        try:
            dev_node = entry.resolve()
        except OSError:
            continue
        mount = _find_mount(dev_node) or _find_mount(Path(str(dev_node) + '1'))
        devices.append(RodeDevice(serial=serial, mount_point=mount,
                                  name='', by_id_path=entry))
    return devices
def mic_style(dev: RodeDevice, devices: list) -> str:
    idx = next((i for i, d in enumerate(devices) if d.serial == dev.serial), 0)
    return MIC_STYLES[idx % len(MIC_STYLES)]
def resolve_names(devices: list, cfg: dict, auto_yes: bool = False) -> list:
    """
    Match each detected device to a saved name. For unknown serials:
      - interactive mode: prompt user
      - auto_yes mode: assign TX-{last4} automatically and save
    """
    changed = False
    for dev in devices:
        if dev.serial in cfg:
            dev.name = cfg[dev.serial]['name']
        else:
            if auto_yes:
                # Non-interactive: auto-name as TX-{last4}
                auto_name = f"TX-{dev.serial[-4:]}"
                dev.name = auto_name
                cfg[dev.serial] = {
                    'name': auto_name, 'serial': dev.serial,
                    'first_seen': datetime.now().isoformat(),
                    'auto_named': True,
                }
                changed = True
                console.print(f"  [yellow]New device auto-named:[/yellow] "
                              f"[bold cyan]{auto_name}[/bold cyan] "
                              f"([dim]serial {dev.serial}[/dim])")
            else:
                console.print()
                console.print(Panel(
                    f"[bold yellow]New device detected![/bold yellow]\n\n"
                    f"  Serial:   [bold cyan]{dev.serial}[/bold cyan]\n"
                    f"  Mounted:  [dim]{dev.mount_point or 'not mounted'}[/dim]\n\n"
                    f"Give this transmitter a name — recognised automatically next time.\n"
                    f"[dim]Examples: Adge, Seraphe, TX1, Lav-Left[/dim]",
                    border_style="yellow", padding=(0, 2)
                ))
                name = Prompt.ask(
                    f"  [bold cyan]Name for {dev.serial}[/bold cyan]",
                    default=f"TX-{dev.serial[-4:]}"
                )
                dev.name = name.strip()
                cfg[dev.serial] = {
                    'name': dev.name, 'serial': dev.serial,
                    'first_seen': datetime.now().isoformat()
                }
                changed = True
    if changed:
        save_config(cfg)
        console.print(f"  [dim]Saved to {CONFIG_PATH}[/dim]")
    return devices
# ── Audio file model ──────────────────────────────────────────────────────────
@dataclass
class AudioFile:
    path:   Path
    device: RodeDevice
    stat:   os.stat_result = field(repr=False)
    @property
    def size(self) -> int:
        return self.stat.st_size
    @property
    def best_date(self) -> datetime:
        return datetime.fromtimestamp(min(self.stat.st_mtime, self.stat.st_ctime))
    @property
    def size_human(self) -> str:
        b = self.size
        for u in ['B', 'KB', 'MB', 'GB']:
            if b < 1024: return f"{b:.1f} {u}"
            b /= 1024
        return f"{b:.1f} TB"
    def fingerprint(self) -> str:
        """Quick fingerprint — reads ≤128KB regardless of file size."""
        return quick_fingerprint(self.path, self.size)
def scan_device(dev: RodeDevice) -> list:
    if not dev.mount_point or not dev.mount_point.exists():
        return []
    files = []
    for p in sorted(dev.mount_point.rglob('*')):
        if p.is_file() and p.suffix in AUDIO_EXTENSIONS:
            try:
                s = p.stat()
                if s.st_size > 0:
                    files.append(AudioFile(path=p, device=dev, stat=s))
            except OSError:
                pass
    return files
# ── Naming ────────────────────────────────────────────────────────────────────
def build_dest_name(af: AudioFile, used: set) -> str:
    dt    = af.best_date
    pfx   = dt.strftime('%Y%m%d_%H%M%S')
    mic   = ''.join(c if c.isalnum() or c in '-_' else '_' for c in af.device.name)
    stem  = af.path.stem
    ext   = af.path.suffix or '.wav'
    base  = f"{pfx}_{mic}_{stem}"
    cand  = f"{base}{ext}"
    if cand not in used:
        return cand
    for c in 'bcdefghijklmnopqrstuvwxyz':
        cand = f"{base}_{c}{ext}"
        if cand not in used:
            return cand
    return f"{base}_{dt.strftime('%f')}{ext}"
def dest_path_for(af: AudioFile, base_dir: Path, dest_name: str) -> Path:
    subdir = month_subdir(af.best_date)
    return base_dir / subdir / dest_name
# ── Display helpers ───────────────────────────────────────────────────────────
def show_banner():
    console.print(Align.center(BANNER))
    console.print(Rule(style="dim cyan"))
def show_step(label: str):
    console.print()
    console.print(Rule(f"[bold]{label}[/bold]", style="dim"))
    console.print()
def show_devices(devices: list):
    t = Table(title="[bold]Detected RØDE Transmitters[/bold]",
              box=box.SIMPLE_HEAVY, border_style="cyan", expand=True)
    t.add_column("Name",        style="bold",  width=14)
    t.add_column("Serial",      style="cyan",  width=12)
    t.add_column("Mount point", style="white")
    t.add_column("Status",      justify="center", width=12)
    for dev in devices:
        st      = mic_style(dev, devices)
        mounted = dev.mount_point is not None
        t.add_row(
            f"[{st}]{dev.name}[/{st}]",
            dev.serial,
            str(dev.mount_point) if mounted else '[dim]—[/dim]',
            "[green]mounted[/green]" if mounted else "[red]not mounted[/red]",
        )
    console.print(t)
def show_scan_results(all_files: list, new_files: list, skip_files: list,
                      devices: list):
    t = Table(title="[bold]Scan Results[/bold]",
              box=box.SIMPLE_HEAVY, border_style="cyan",
              show_lines=True, expand=True)
    t.add_column("Status",         style="bold", width=10, justify="center")
    t.add_column("Mic",            style="bold", width=12, justify="center")
    t.add_column("Filename",       style="white", min_width=24)
    t.add_column("Size",           style="yellow", justify="right", width=10)
    t.add_column("Recording date", style="green",  width=22)
    for af, fp in new_files:
        st = mic_style(af.device, devices)
        t.add_row(
            "[bold green]NEW[/bold green]",
            f"[{st}]{af.device.name}[/{st}]",
            af.path.name,
            af.size_human,
            af.best_date.strftime('%Y-%m-%d  %H:%M:%S'),
        )
    for af, fp in skip_files:
        st = mic_style(af.device, devices)
        t.add_row(
            "[dim]skip[/dim]",
            f"[{st}]{af.device.name}[/{st}]",
            af.path.name,
            af.size_human,
            af.best_date.strftime('%Y-%m-%d  %H:%M:%S'),
        )
    console.print(t)
def show_plan(plan: list, devices: list, base_dir: Path):
    t = Table(title="[bold]Transfer Plan[/bold]",
              box=box.SIMPLE_HEAVY, border_style="green",
              show_lines=True, expand=True)
    t.add_column("Mic",          style="bold", width=12, justify="center")
    t.add_column("Original",     style="white", min_width=20)
    t.add_column("→ Destination", style="bold green", min_width=54)
    t.add_column("Size",         style="yellow", justify="right", width=10)
    t.add_column("Date",         style="dim", width=12)
    for af, dest_name, fp in plan:
        st = mic_style(af.device, devices)
        full_dest = f"{month_subdir(af.best_date)}/{dest_name}"
        t.add_row(
            f"[{st}]{af.device.name}[/{st}]",
            af.path.name,
            full_dest,
            af.size_human,
            af.best_date.strftime('%Y-%m-%d'),
        )
    console.print(t)
# ── Transfer ──────────────────────────────────────────────────────────────────
def do_transfer(plan: list, base_dir: Path, manifest: Manifest, dry_run: bool = False):
    stats = {'copied': 0, 'errors': [], 'total_bytes': 0}
    progress = Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=36, style="cyan", complete_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        FileSizeColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console, expand=True,
    )
    overall = progress.add_task("Overall", total=len(plan))
    with progress:
        for af, dest_name, fp in plan:
            dest_full = dest_path_for(af, base_dir, dest_name)
            ftask = progress.add_task(f"[dim]{dest_name[:48]}[/dim]", total=af.size)
            try:
                if not dry_run:
                    dest_full.parent.mkdir(parents=True, exist_ok=True)
                    with open(af.path, 'rb') as src, open(dest_full, 'wb') as dst:
                        while data := src.read(CHUNK_SIZE):
                            dst.write(data)
                            progress.update(ftask, advance=len(data))
                    os.utime(dest_full, (af.stat.st_atime, af.stat.st_mtime))
                    if fp is not None:
                        manifest.record(fp, f"{month_subdir(af.best_date)}/{dest_name}",
                                        af.size, af.device.name)
                else:
                    progress.update(ftask, advance=af.size)
                stats['copied']      += 1
                stats['total_bytes'] += af.size
                st = mic_style(af.device, [af.device])
                console.print(f"  [green]✓[/green] [{st}]{af.device.name}[/{st}] → {month_subdir(af.best_date)}/{dest_name}")
            except Exception as e:
                stats['errors'].append((dest_name, str(e)))
                console.print(f"  [red]✗[/red] {dest_name}: {e}")
            progress.update(overall, advance=1)
            progress.remove_task(ftask)
    if not dry_run:
        manifest.save()
    return stats
# ── Utility commands ──────────────────────────────────────────────────────────
def cmd_list_devices(cfg: dict):
    if not cfg:
        console.print("[yellow]No devices saved yet. Plug in a mic and run rode-transfer.[/yellow]")
        return
    t = Table(title="[bold]Known RØDE Devices[/bold]",
              box=box.SIMPLE_HEAVY, border_style="cyan", expand=False)
    t.add_column("Name",       style="bold cyan")
    t.add_column("Serial",     style="dim")
    t.add_column("First seen", style="dim")
    for serial, info in cfg.items():
        t.add_row(info['name'], serial, info.get('first_seen', '—')[:10])
    console.print(t)
    console.print(f"\n  [dim]Saved at: {CONFIG_PATH}[/dim]")
# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description='RØDE Wireless GO — dual-mic transfer with dedup '
                    '(auto-identifies by USB serial)',
    )
    ap.add_argument('--dest',         type=Path,
                    help='Base destination directory (files sorted into YYYY/MM-Month subfolders)')
    ap.add_argument('--dry-run',      action='store_true',
                    help='Preview only — nothing copied')
    ap.add_argument('--list-devices', action='store_true',
                    help='Show saved device names and exit')
    ap.add_argument('--forget',       metavar='SERIAL',
                    help='Remove a device name from config')
    ap.add_argument('--fast',         action='store_true',
                    help='Skip hashing — dedup by filename pattern only (fastest)')
    ap.add_argument('--no-banner',    action='store_true')
    ap.add_argument('--yes', '-y',    action='store_true',
                    help='Non-interactive: assume defaults, auto-name unknown TX, skip confirms')
    args = ap.parse_args()
    cfg = load_config()
    if args.list_devices:
        cmd_list_devices(cfg); return
    if args.forget:
        if args.forget in cfg:
            name = cfg.pop(args.forget)['name']
            save_config(cfg)
            console.print(f"[green]Removed:[/green] {args.forget} ({name})")
        else:
            console.print(f"[yellow]Serial not found:[/yellow] {args.forget}")
        return
    # --yes implies --no-banner for cleaner automation logs
    if args.yes:
        args.no_banner = True
    # ── Banner ────────────────────────────────────────────────────────────────
    if not args.no_banner:
        show_banner()
    console.print()
    console.print(Panel(
        "[bold white]Auto-identifies RØDE transmitters by USB serial number.\n"
        "Dedup via quick fingerprint — only new recordings are copied.\n"
        "Files sorted into year/month folders by recording date.\n"
        "Device files are never deleted — firmware handles cleanup.[/bold white]",
        border_style="cyan", padding=(0, 2),
    ))
    if args.dry_run:
        console.print()
        console.print(Panel(
            "[bold yellow]DRY RUN — nothing will be copied[/bold yellow]",
            border_style="yellow",
        ))
    # ── Discover devices ──────────────────────────────────────────────────────
    show_step("Detecting RØDE Devices")
    with console.status("[cyan]Scanning /dev/disk/by-id/ for RØDE transmitters...[/cyan]"):
        devices = find_rode_devices()
    if not devices:
        console.print(Panel(
            "[red]No RØDE Wireless GO transmitters found.[/red]\n\n"
            "[dim]• Plug in the mic via USB-C — it should mount as mass storage\n"
            f"• Expected in /dev/disk/by-id/ as:  usb-RODE_Wireless_GO_*[/dim]",
            border_style="red",
        ))
        sys.exit(1)
    devices = resolve_names(devices, cfg, auto_yes=args.yes)
    console.print()
    show_devices(devices)
    mounted = [d for d in devices if d.mount_point]
    if not mounted:
        console.print("\n[red]Detected device(s) are not mounted — cannot read files.[/red]")
        sys.exit(1)
    # ── Destination ───────────────────────────────────────────────────────────
    console.print()
    base_dir = args.dest
    if not base_dir:
        if args.yes:
            base_dir = DEFAULT_DEST
        else:
            raw  = Prompt.ask("[bold cyan]Base directory[/bold cyan]\n"
                              "[dim](files auto-sort into YYYY/MM-Month subfolders)[/dim]",
                              default=str(DEFAULT_DEST))
            base_dir = Path(raw).expanduser().resolve()
    console.print(f"  [green]Base directory:[/green] {base_dir}")
    console.print(f"  [dim]Files will be sorted into {base_dir}/YYYY/MM-Month/ by recording date[/dim]")
    # ── Load manifest ─────────────────────────────────────────────────────────
    manifest = Manifest(base_dir)
    console.print(f"  [green]Manifest:[/green] {manifest.path} ({manifest.count} known files)")
    # ── Scan files ────────────────────────────────────────────────────────────
    show_step("Scanning Audio Files")
    all_files = []
    for dev in mounted:
        with console.status(f"[cyan]Scanning {dev.name} ({dev.serial})...[/cyan]"):
            files = scan_device(dev)
        st = mic_style(dev, devices)
        console.print(
            f"  [{st}]{dev.name}[/{st}] [dim]({dev.serial})[/dim]  →  "
            f"[bold]{len(files)}[/bold] file(s) on device"
        )
        all_files.extend(files)
    if not all_files:
        console.print("\n[yellow]No audio files found on any mounted device.[/yellow]")
        sys.exit(0)
    # ── Classify ─────────────────────────────────────────────────────────────
    new_files  = []
    skip_files = []
    if args.fast:
        show_step("Fast Dedup (filename match only — no hashing)")
        existing = set()
        if base_dir.exists():
            for p in base_dir.rglob('*'):
                if p.is_file() and not p.name.startswith('.'):
                    existing.add(p.name)
        for af in all_files:
            mic = ''.join(c if c.isalnum() or c in '-_' else '_' for c in af.device.name)
            stem = af.path.stem
            pattern = f"_{mic}_{stem}"
            already = any(f.endswith(pattern + af.path.suffix) or
                         f.endswith(pattern + af.path.suffix.lower()) or
                         f.endswith(pattern + af.path.suffix.upper())
                         for f in existing)
            if already:
                skip_files.append((af, None))
            else:
                new_files.append((af, None))
        console.print(f"  [dim]Checked {len(all_files)} files against {len(existing)} "
                      f"existing filenames — zero bytes read[/dim]")
    else:
        show_step("Fingerprinting (≤128KB per file)")
        fp_progress = Progress(
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=36, style="cyan", complete_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("{task.completed}/{task.total}"),
            console=console, expand=True,
        )
        fptask = fp_progress.add_task("Fingerprinting files...", total=len(all_files))
        with fp_progress:
            for af in all_files:
                fp = af.fingerprint()
                if manifest.has_fingerprint(fp):
                    skip_files.append((af, fp))
                else:
                    new_files.append((af, fp))
                fp_progress.advance(fptask)
    console.print()
    show_scan_results(all_files, new_files, skip_files, devices)
    new_total = sum(af.size for af, _ in new_files)
    new_h = f"{new_total/(1024**3):.2f} GB" if new_total > 1024**3 else f"{new_total/(1024**2):.1f} MB"
    skip_total = sum(af.size for af, _ in skip_files)
    skip_h = f"{skip_total/(1024**3):.2f} GB" if skip_total > 1024**3 else f"{skip_total/(1024**2):.1f} MB"
    console.print()
    console.print(Panel(
        f"[bold green]{len(new_files)}[/bold green] new file(s) ({new_h})\n"
        f"[dim]{len(skip_files)} already imported ({skip_h}) — skipping[/dim]",
        border_style="green" if new_files else "dim",
    ))
    if not new_files:
        console.print("[green]All files already imported. Nothing to do.[/green]")
        sys.exit(0)
    # ── Build plan ────────────────────────────────────────────────────────────
    show_step("Building Transfer Plan")
    used: set = set()
    if base_dir.exists():
        for p in base_dir.rglob('*'):
            if p.is_file() and not p.name.startswith('.'):
                used.add(p.name)
    plan = []
    for af, fp in sorted(new_files, key=lambda x: (x[0].best_date, x[0].device.name)):
        name = build_dest_name(af, used)
        used.add(name)
        plan.append((af, name, fp))
    show_plan(plan, devices, base_dir)
    console.print()
    months = {}
    for af, name, fp in plan:
        m = month_subdir(af.best_date)
        months[m] = months.get(m, 0) + 1
    for m in sorted(months):
        console.print(f"  [dim]{base_dir}/{m}/[/dim]  →  [bold]{months[m]}[/bold] file(s)")
    console.print(f"\n  [bold]Total:[/bold] {len(plan)} new file(s) · {new_h}")
    if args.dry_run:
        console.print()
        console.print("[yellow]DRY RUN — stopping here. No files copied.[/yellow]")
        sys.exit(0)
    # ── Confirm ───────────────────────────────────────────────────────────────
    console.print()
    if not args.yes:
        if not Confirm.ask(f"[bold green]Copy {len(plan)} new file(s) → {base_dir}/...?[/bold green]",
                           default=True):
            console.print("[dim]Aborted.[/dim]")
            sys.exit(0)
    else:
        console.print(f"[dim]--yes: proceeding without confirmation[/dim]")
    # ── Transfer ──────────────────────────────────────────────────────────────
    show_step("Transferring")
    stats = do_transfer(plan, base_dir, manifest)
    # ── Summary ───────────────────────────────────────────────────────────────
    console.print()
    console.print(Rule(style="dim"))
    sc = "green" if not stats['errors'] else "yellow"
    console.print(Panel(
        f"[bold {sc}]Transfer complete[/bold {sc}]\n\n"
        f"  Copied:   [bold]{stats['copied']}[/bold] new file(s)\n"
        f"  Skipped:  [bold]{len(skip_files)}[/bold] (already imported)\n"
        f"  Errors:   [bold]{len(stats['errors'])}[/bold]\n"
        f"  Total:    [bold]{stats['total_bytes']/(1024**2):.1f} MB[/bold]\n"
        f"  Manifest: [bold]{manifest.count}[/bold] files tracked",
        border_style=sc, padding=(1, 4),
    ))
    if stats['errors']:
        console.print("\n[red]Copy errors:[/red]")
        for name, err in stats['errors']:
            console.print(f"  [red]✗[/red] {name}: {err}")
    console.print(f"\n  Files saved to: [bold green]{base_dir}/YYYY/MM-Month/[/bold green]\n")
if __name__ == '__main__':
    main()
