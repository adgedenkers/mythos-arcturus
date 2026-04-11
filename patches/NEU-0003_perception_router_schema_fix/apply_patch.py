import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=3,
    description='perception router schema fix',
    patch_type='FIX'
)

patch.begin()

router_file = Path("/opt/mythos/neuro/perception_router.py")

text = router_file.read_text()

old_sql = """
                INSERT INTO perception_log
                (event_type, content, source, metadata, created_at)
                VALUES (%s,%s,%s,%s,%s)
                RETURNING id
"""

new_sql = """
                INSERT INTO perception_log
                (source, source_platform, content, raw_data)
                VALUES (%s,%s,%s,%s)
                RETURNING id
"""

text = text.replace(old_sql, new_sql)

router_file.write_text(text)

patch.finish()
