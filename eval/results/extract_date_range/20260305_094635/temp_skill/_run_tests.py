#!/usr/bin/env python3
import sys, json, asyncio, traceback
sys.path.insert(0, '/opt/mythos/skills')
sys.path.insert(0, '/opt/mythos/eval/results/extract_date_range/20260305_094635/temp_skill')
results = []
try:
    import importlib.util
    spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/extract_date_range/20260305_094635/temp_skill/test_skill.py")
    module = importlib.util.module_from_spec(spec_obj)
    spec_obj.loader.exec_module(module)
    from engine.base import SkillBase, SkillRequest
    skill_class = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
            skill_class = attr
            break
    if not skill_class:
        print(json.dumps({"error": "No SkillBase subclass", "results": []}))
        sys.exit(0)
    instance = skill_class()
    with open("/opt/mythos/eval/results/extract_date_range/20260305_094635/temp_skill/_test_cases.json") as _tc_f:
        test_cases = json.load(_tc_f)
    async def run():
        for i, tc in enumerate(test_cases):
            tr = {"test_index": i, "message": tc["message"], "passed": [], "failed": []}
            try:
                req = SkillRequest(message=tc["message"])
                resp = await instance.run(req)
                if "expect_ok" in tc:
                    if resp.ok == tc["expect_ok"]:
                        tr["passed"].append(f"ok={resp.ok}")
                    else:
                        tr["failed"].append(f"Expected ok={tc['expect_ok']}, got {resp.ok} (error: {resp.error})")
                for kw in tc.get("expect_summary_contains", []):
                    if kw.lower() in resp.summary.lower():
                        tr["passed"].append(f"summary has '{kw}'")
                    else:
                        tr["failed"].append(f"summary missing '{kw}': {resp.summary[:200]}")
                for key in tc.get("expect_data_has", []):
                    if key in resp.data:
                        tr["passed"].append(f"data has '{key}'")
                    else:
                        tr["failed"].append(f"data missing '{key}': {list(resp.data.keys())}")
                if resp.summary:
                    tr["passed"].append("summary non-empty")
                else:
                    tr["failed"].append("summary empty")
            except Exception as e:
                tr["failed"].append(f"Error: {e}")
            results.append(tr)
    asyncio.run(run())
except Exception as e:
    results = [{"test_index": -1, "passed": [], "failed": [f"Setup error: {e}"]}]
print(json.dumps({"results": results}))
