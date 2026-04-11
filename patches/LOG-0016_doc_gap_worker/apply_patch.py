import sys
import os
import stat

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=16,
    description='doc_gap_worker',
    patch_type='MINOR',
)
patch.begin()

# --- Deploy mythos-doc-gap CLI ---
patch.deploy_file(
    'opt/mythos/bin/mythos-doc-gap',
    '/opt/mythos/bin/mythos-doc-gap',
)
os.chmod('/opt/mythos/bin/mythos-doc-gap', 0o755)

# --- Fix LLM model in doc worker (iris-thinking-v2 → qwen2.5:32b) ---
# iris-thinking-v2 timed out on all benchmark tasks. qwen2.5:32b is the
# proven winner at 81.1% across 43 tasks.
llm_path = '/opt/mythos/iris/docs/llm.py'
with open(llm_path, 'r') as f:
    content = f.read()

old_model = 'MODEL = "iris-thinking-v2"'
new_model = 'MODEL = "qwen2.5:32b"'

if old_model in content:
    content = content.replace(old_model, new_model)
    with open(llm_path, 'w') as f:
        f.write(content)
    print(f"  ✓ Updated LLM model: iris-thinking-v2 → qwen2.5:32b")
else:
    if new_model in content:
        print(f"  ✓ LLM model already set to qwen2.5:32b")
    else:
        print(f"  ⚠ Could not find model line in {llm_path}")

# --- Syntax check ---
import py_compile
py_compile.compile('/opt/mythos/bin/mythos-doc-gap', doraise=True)
print("  ✓ mythos-doc-gap syntax OK")

py_compile.compile(llm_path, doraise=True)
print(f"  ✓ {llm_path} syntax OK")

patch.finish()
