#!/usr/bin/env python3
"""
tweak.py — Quick personality adjustment tool
=============================================
Modify personality sliders in test presets or production config.

Usage:
  tweak.py show                                   # Show production sliders
  tweak.py show tars_75                            # Show a preset
  tweak.py set humor 75                            # Set production slider
  tweak.py set humor 75 truth 100                  # Set multiple
  tweak.py set humor 75 --preset tars_75           # Modify a preset file
  tweak.py create my_custom --from default --set humor 90 warmth 100
  tweak.py reset                                   # Reset production to defaults
  tweak.py list                                    # List all presets
"""
import argparse
import sys
import copy
from pathlib import Path

import yaml

PROD_PERSONALITY = Path("/opt/mythos/prompts/personality.yaml")
LAB_DIR = Path(__file__).parent
PRESETS_DIR = LAB_DIR / "personalities"

VALID_SLIDERS = [
    'verbosity', 'warmth', 'humor', 'truth', 'speculation',
    'autonomy', 'mystical', 'formality', 'challenge'
]

SLIDER_EMOJIS = {
    'verbosity': '📏', 'warmth': '🌡️', 'humor': '😏', 'truth': '⚡',
    'speculation': '🔮', 'autonomy': '🧭', 'mystical': '✨',
    'formality': '👔', 'challenge': '⚔️'
}


def load_yaml(path):
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def save_yaml(path, data):
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def render_bar(value, width=20):
    filled = int(value / 100 * width)
    return '█' * filled + '░' * (width - filled)


def show_sliders(sliders, title=""):
    if title:
        print(f"\n{title}")
        print("-" * 50)
    for k in VALID_SLIDERS:
        v = sliders.get(k, 50)
        emoji = SLIDER_EMOJIS.get(k, '•')
        bar = render_bar(v)
        print(f"  {emoji} {k:<14} {bar} {v:>3}")


def cmd_show(args):
    if args.target:
        # Show a preset
        path = PRESETS_DIR / f"{args.target}.yaml"
        if not path.exists():
            print(f"❌ Preset not found: {args.target}")
            print(f"   Available: {', '.join(p.stem for p in PRESETS_DIR.glob('*.yaml'))}")
            sys.exit(1)
        data = load_yaml(path)
        show_sliders(data.get('sliders', {}), f"Preset: {args.target} — {data.get('description', '')}")
    else:
        # Show production
        data = load_yaml(PROD_PERSONALITY)
        show_sliders(data.get('sliders', {}), "Production (personality.yaml)")


def cmd_set(args):
    pairs = args.pairs
    if len(pairs) % 2 != 0:
        print("❌ Need pairs: slider value slider value ...")
        sys.exit(1)

    changes = {}
    for i in range(0, len(pairs), 2):
        name = pairs[i].lower()
        try:
            value = int(pairs[i + 1])
        except ValueError:
            print(f"❌ Value must be a number: {pairs[i + 1]}")
            sys.exit(1)

        if name not in VALID_SLIDERS:
            print(f"❌ Unknown slider: {name}")
            print(f"   Valid: {', '.join(VALID_SLIDERS)}")
            sys.exit(1)

        value = max(0, min(100, value))
        changes[name] = value

    if args.preset:
        path = PRESETS_DIR / f"{args.preset}.yaml"
        if not path.exists():
            print(f"❌ Preset not found: {args.preset}")
            sys.exit(1)
        data = load_yaml(path)
        for k, v in changes.items():
            data.setdefault('sliders', {})[k] = v
        save_yaml(path, data)
        print(f"✅ Updated preset '{args.preset}':")
    else:
        data = load_yaml(PROD_PERSONALITY)
        for k, v in changes.items():
            data.setdefault('sliders', {})[k] = v
        save_yaml(PROD_PERSONALITY, data)
        print("✅ Updated production personality.yaml:")

    for k, v in changes.items():
        emoji = SLIDER_EMOJIS.get(k, '•')
        print(f"  {emoji} {k} → {v}")


def cmd_create(args):
    base_name = args.base or 'default'
    base_path = PRESETS_DIR / f"{base_name}.yaml"
    if not base_path.exists():
        print(f"❌ Base preset not found: {base_name}")
        sys.exit(1)

    base = load_yaml(base_path)
    new_data = copy.deepcopy(base)
    new_data['name'] = args.name
    new_data['description'] = f"Custom preset based on {base_name}"

    if args.set_values:
        pairs = args.set_values
        if len(pairs) % 2 != 0:
            print("❌ --set needs pairs: slider value slider value ...")
            sys.exit(1)
        for i in range(0, len(pairs), 2):
            name = pairs[i].lower()
            try:
                value = max(0, min(100, int(pairs[i + 1])))
            except ValueError:
                print(f"❌ Value must be a number: {pairs[i + 1]}")
                sys.exit(1)
            if name not in VALID_SLIDERS:
                print(f"❌ Unknown slider: {name}")
                sys.exit(1)
            new_data.setdefault('sliders', {})[name] = value

    out_path = PRESETS_DIR / f"{args.name}.yaml"
    save_yaml(out_path, new_data)
    show_sliders(new_data.get('sliders', {}), f"Created: {args.name}")


def cmd_reset(args):
    defaults = {
        'sliders': {
            'verbosity': 75, 'warmth': 75, 'humor': 35, 'truth': 90,
            'speculation': 65, 'autonomy': 50, 'mystical': 70,
            'formality': 25, 'challenge': 55,
        }
    }
    save_yaml(PROD_PERSONALITY, defaults)
    show_sliders(defaults['sliders'], "Production reset to defaults")


def cmd_list(args):
    print("Available personality presets:")
    print("-" * 60)
    for f in sorted(PRESETS_DIR.glob('*.yaml')):
        data = load_yaml(f)
        desc = data.get('description', '')
        print(f"  {f.stem:<20} {desc}")
    print(f"\nProduction config: {PROD_PERSONALITY}")


def main():
    parser = argparse.ArgumentParser(description="Quick personality slider adjustment")
    sub = parser.add_subparsers(dest='command')

    # show
    p_show = sub.add_parser('show', help='Show current sliders')
    p_show.add_argument('target', nargs='?', help='Preset name (default: production)')

    # set
    p_set = sub.add_parser('set', help='Set slider values')
    p_set.add_argument('pairs', nargs='+', help='slider value pairs')
    p_set.add_argument('--preset', help='Modify a preset instead of production')

    # create
    p_create = sub.add_parser('create', help='Create a new preset')
    p_create.add_argument('name', help='New preset name')
    p_create.add_argument('--from', dest='base', default='default', help='Base preset')
    p_create.add_argument('--set', dest='set_values', nargs='+', help='Override sliders')

    # reset
    sub.add_parser('reset', help='Reset production to defaults')

    # list
    sub.add_parser('list', help='List all presets')

    args = parser.parse_args()

    if args.command == 'show':
        cmd_show(args)
    elif args.command == 'set':
        cmd_set(args)
    elif args.command == 'create':
        cmd_create(args)
    elif args.command == 'reset':
        cmd_reset(args)
    elif args.command == 'list':
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
