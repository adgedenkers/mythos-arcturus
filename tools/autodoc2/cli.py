#!/opt/mythos/.venv/bin/python3
"""
AutoDoc2 CLI.

Usage:
  autodoc2 [TARGET] [options]

Examples:
  # Crawl Mythos itself (default target, default env, default output)
  autodoc2

  # Crawl an external repo into the demo-live Neo4j, output to that repo's .autodoc2/
  autodoc2 /tmp/requests --env-file /opt/mythos/.env.demo-live

  # Crawl with custom output dir, no LLM summaries, verbose
  autodoc2 /tmp/strapi --output-dir /tmp/strapi-docs --skip-llm --verbose

  # Wipe an existing crawl and re-run
  autodoc2 /tmp/requests --env-file /opt/mythos/.env.demo-live --clean

  # Full crawl with gemma4:26b structural analysis per file (SYS-0087)
  autodoc2 --analyze

  # Analysis only, no markdown output
  autodoc2 --analyze --skip-llm
"""

import argparse
import sys
from pathlib import Path

# Allow running as a script from /opt/mythos/bin/autodoc2 symlink
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, '/opt/mythos/tools')
    __package__ = 'autodoc2'

from .config import load_config
from .engine import AutodocEngine
from .walkers import supported_languages
from . import __version__


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog='autodoc2',
        description='Multi-language codebase documentation engine for Mythos.',
    )
    p.add_argument(
        'target',
        nargs='?',
        default='/opt/mythos',
        help='Directory to crawl (default: /opt/mythos)',
    )
    p.add_argument(
        '--output-dir', '-o',
        default=None,
        help='Markdown output directory (default: <target>/.autodoc2/, '
             'or /opt/mythos/docs/autodoc2/ when target is /opt/mythos)',
    )
    p.add_argument(
        '--env-file', '-e',
        default='/opt/mythos/.env',
        help='Path to .env file with NEO4J_URI/USER/PASSWORD (default: /opt/mythos/.env)',
    )
    p.add_argument(
        '--include',
        action='append',
        default=[],
        help='Glob pattern to include (relative to target). Can be passed multiple times.',
    )
    p.add_argument(
        '--exclude',
        action='append',
        default=[],
        help='Glob pattern to exclude. Can be passed multiple times.',
    )
    p.add_argument('--clean', action='store_true',
                   help='Delete existing crawl data for this target before running')
    p.add_argument('--resume', action='store_true',
                   help='(reserved for future use)')
    p.add_argument('--skip-llm', action='store_true',
                   help='Do not generate markdown summaries via Ollama')
    p.add_argument(
        '--analyze', '-a',
        action='store_true',
        help='Run gemma4:26b structural analysis per file (SYS-0087). '
             'Opt-in: adds ~1-3s per file. Results stored as analysis_* '
             'properties on AutodocFile nodes in Neo4j.',
    )
    p.add_argument('--verbose', '-v', action='store_true',
                   help='Print one line per file processed')
    p.add_argument('--status', action='store_true',
                   help='Print supported languages and exit')
    p.add_argument('--version', action='version', version=f'autodoc2 {__version__}')
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.status:
        print(f"autodoc2 {__version__}")
        print(f"supported languages: {', '.join(supported_languages())}")
        return 0

    target = Path(args.target)
    output_dir = Path(args.output_dir) if args.output_dir else None
    env_file = Path(args.env_file)

    cfg = load_config(
        target=target,
        output_dir=output_dir,
        env_file=env_file,
        include=args.include,
        exclude=args.exclude,
        clean=args.clean,
        resume=args.resume,
        skip_llm=args.skip_llm,
        verbose=args.verbose,
        analyze=args.analyze,
    )

    engine = AutodocEngine(cfg)
    return engine.run()


if __name__ == "__main__":
    sys.exit(main())
