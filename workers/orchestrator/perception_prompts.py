"""Perception system prompt — loaded by orchestrator."""

# This will be loaded from perception_template.yaml in production.
# For now, copy from the test suite's SYSTEM_PROMPT.
# TODO: Build yaml loader that extracts system_prompt from template files.

import os

def _load_from_test_suite():
    """Temporary: extract SYSTEM_PROMPT from test suite."""
    path = "/opt/mythos/workers/tests/perception_test_suite.py"
    if os.path.exists(path):
        with open(path) as f:
            content = f.read()
        # Extract between triple quotes
        start = content.find('SYSTEM_PROMPT = """') + len('SYSTEM_PROMPT = """')
        end = content.find('"""', start)
        if start > 0 and end > 0:
            return content[start:end]
    return "You are a perception processor. Output JSON."

PERCEPTION_SYSTEM_PROMPT = _load_from_test_suite()
