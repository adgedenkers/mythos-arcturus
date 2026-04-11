import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=19,
    description='Auto bill matching after CSV import — wire PostImportAnalyzer into importer.py',
    patch_type='MINOR',
)
patch.begin()

IMP_PATH = '/opt/mythos/finance/importer.py'

with open(IMP_PATH, 'r') as f:
    imp = f.read()

# The exact block with blank lines between sections
old_block = """        if not args.dry_run and not args.no_archive:
            archive_path = archive_file(args.file, args.bank)
            print(f"\\nArchived to: {archive_path}")

    finally:
        importer.close()

    print("\\nDone!")"""

new_block = """        if not args.dry_run and not args.no_archive:
            archive_path = archive_file(args.file, args.bank)
            print(f"\\nArchived to: {archive_path}")

        # ── Post-import analysis: bill matching + Telegram report (SYS-0019) ──
        if not args.dry_run and results['imported'] > 0:
            try:
                from post_import_analyzer import PostImportAnalyzer
                analyzer = PostImportAnalyzer()
                report = analyzer.analyze_import(
                    bank=args.bank,
                    imported_count=results['imported'],
                    skipped_count=results['skipped'],
                    source_file=Path(args.file).name,
                    prompt_balance=(args.bank == 'usaa' and args.balance is not None),
                )
                print(f"\\n\\U0001f4cb Bill matching: {len(report['bill_matches'])} matched, "
                      f"{len(report['unpaid_bills'])} unpaid this month")
                for m in report['bill_matches']:
                    print(f"  \\u2713 {m['bill_name']:25} ${m['actual']:>8.2f}")
                analyzer.send_telegram_report(report)
                print("  \\u2192 Telegram report sent")
                analyzer.close()
            except Exception as e:
                print(f"\\n\\u26a0\\ufe0f  Post-import analysis failed (non-fatal): {e}")

    finally:
        importer.close()

    print("\\nDone!")"""

assert old_block in imp, f"Block not found. Looking for:\\n{repr(old_block[:100])}"
imp = imp.replace(old_block, new_block)

with open(IMP_PATH, 'w') as f:
    f.write(imp)

patch.logger.log("importer.py: Wired PostImportAnalyzer after successful import")

import py_compile
py_compile.compile(IMP_PATH, doraise=True)
patch.logger.log("importer.py compiles OK")

patch.finish()
