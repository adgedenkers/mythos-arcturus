import sys
import os
import shutil
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=6,
    description='idle_task_engine (loop.py wiring)',
    patch_type='PATCH',
)
patch.begin()

# --- Wire into loop.py using str.replace ---
# Files and SQL already deployed by first run.
# This patch only does the loop.py edits.

loop_path = '/opt/mythos/iris/core/src/loop.py'

# Read current content
with open(loop_path, 'r') as f:
    content = f.read()

# Backup
backup_path = loop_path + f'.bak.{patch.timestamp}'
shutil.copy2(loop_path, backup_path)
patch.logger.log(f"  ✓ backup: {backup_path}")

original = content  # keep for rollback

# Edit 1: Add import for task_registry
old1 = 'from .agency import AgencySystem\nfrom .llm import LLMClient'
new1 = 'from .agency import AgencySystem\nfrom .llm import LLMClient\nfrom .task_registry import TaskRegistry'

if old1 not in content:
    if 'from .task_registry import TaskRegistry' in content:
        patch.logger.log("  · import already present, skipping")
    else:
        patch.errors.append(f"Edit 1: old string not found in loop.py")
        patch.finish()
        sys.exit(1)
else:
    content = content.replace(old1, new1, 1)
    patch.logger.log("  ✓ edit 1: added task_registry import")

# Edit 2: Add _task_registry to __init__
old2 = '        # Task queue for self-directed work\n        self._task_queue: asyncio.Queue = asyncio.Queue()'
new2 = ('        # Task queue for self-directed work\n'
        '        self._task_queue: asyncio.Queue = asyncio.Queue()\n'
        '        \n'
        '        # Idle task registry (background maintenance)\n'
        '        self._task_registry: Optional[TaskRegistry] = None')

if old2 not in content:
    if '_task_registry' in content:
        patch.logger.log("  · _task_registry field already present, skipping")
    else:
        patch.errors.append(f"Edit 2: old string not found in loop.py")
        with open(loop_path, 'w') as f:
            f.write(original)
        patch.finish()
        sys.exit(1)
else:
    content = content.replace(old2, new2, 1)
    patch.logger.log("  ✓ edit 2: added _task_registry field")

# Edit 3: Initialize task registry in initialize()
old3 = ('        # Initialize agency (how Iris acts)\n'
        '        self.agency = AgencySystem(self.config, self.llm)\n'
        '        await self.agency.initialize()\n'
        '        \n'
        '        log.info("subsystems_initialized")')
new3 = ('        # Initialize agency (how Iris acts)\n'
        '        self.agency = AgencySystem(self.config, self.llm)\n'
        '        await self.agency.initialize()\n'
        '        \n'
        '        # Initialize idle task registry\n'
        '        db_config = {\n'
        '            "host": self.config.postgres_host,\n'
        '            "port": self.config.postgres_port,\n'
        '            "database": self.config.postgres_db,\n'
        '            "user": self.config.postgres_user,\n'
        '            "password": self.config.postgres_password,\n'
        '        }\n'
        '        self._task_registry = TaskRegistry(db_config)\n'
        '        self._task_registry.initialize()\n'
        '        \n'
        '        log.info("subsystems_initialized")')

if old3 not in content:
    if '_task_registry = TaskRegistry' in content:
        patch.logger.log("  · task registry init already present, skipping")
    else:
        patch.errors.append(f"Edit 3: old string not found in loop.py")
        with open(loop_path, 'w') as f:
            f.write(original)
        patch.finish()
        sys.exit(1)
else:
    content = content.replace(old3, new3, 1)
    patch.logger.log("  ✓ edit 3: added task registry initialization")

# Edit 4: Wire idle tasks into _maybe_initiate()
old4 = ('        # Don\'t initiate during PRESENCE mode (human is talking)\n'
        '        if self.state.mode == Mode.PRESENCE:\n'
        '            return\n'
        '        \n'
        '        # Check if there\'s a task to work on\n'
        '        if not self._task_queue.empty() and self.state.mode == Mode.REFLECTION:\n'
        '            task = await self._task_queue.get()\n'
        '            await self._execute_task(task)\n'
        '            return')
new4 = ('        # Don\'t initiate during PRESENCE mode (human is talking)\n'
        '        if self.state.mode == Mode.PRESENCE:\n'
        '            return\n'
        '        \n'
        '        # Check idle task registry for background maintenance\n'
        '        if self._task_registry and self.state.mode in (Mode.BACKGROUND, Mode.REFLECTION):\n'
        '            idle_task = self._task_registry.next_task(self.state.mode.value)\n'
        '            if idle_task:\n'
        '                import time as _time\n'
        '                log.info("executing_idle_task",\n'
        '                         task_type=idle_task.task_type,\n'
        '                         priority=idle_task.priority.name)\n'
        '                _start = _time.time()\n'
        '                try:\n'
        '                    result = idle_task.execute()\n'
        '                except Exception as _e:\n'
        '                    from .task_registry import TaskResult\n'
        '                    result = TaskResult(success=False, error=str(_e))\n'
        '                _elapsed_ms = int((_time.time() - _start) * 1000)\n'
        '                result.metadata["_duration_ms"] = _elapsed_ms\n'
        '                self._task_registry.record_result(idle_task, result)\n'
        '                if result.success:\n'
        '                    self.state.tasks_completed += 1\n'
        '                else:\n'
        '                    self.state.tasks_failed += 1\n'
        '                return\n'
        '        \n'
        '        # Check manual task queue\n'
        '        if not self._task_queue.empty() and self.state.mode == Mode.REFLECTION:\n'
        '            task = await self._task_queue.get()\n'
        '            await self._execute_task(task)\n'
        '            return')

if old4 not in content:
    if 'idle task registry for background maintenance' in content:
        patch.logger.log("  · idle task wiring already present, skipping")
    else:
        patch.errors.append(f"Edit 4: old string not found in loop.py")
        with open(loop_path, 'w') as f:
            f.write(original)
        patch.finish()
        sys.exit(1)
else:
    content = content.replace(old4, new4, 1)
    patch.logger.log("  ✓ edit 4: wired idle tasks into _maybe_initiate()")

# Edit 5: Add idle_tasks_registered to get_state()
old5 = ('            "tasks_completed": self.state.tasks_completed,\n'
        '            "tasks_failed": self.state.tasks_failed,\n'
        '        }')
new5 = ('            "tasks_completed": self.state.tasks_completed,\n'
        '            "tasks_failed": self.state.tasks_failed,\n'
        '            "idle_tasks_registered": len(self._task_registry.tasks) if self._task_registry else 0,\n'
        '        }')

if old5 not in content:
    if 'idle_tasks_registered' in content:
        patch.logger.log("  · idle_tasks_registered already present, skipping")
    else:
        patch.errors.append(f"Edit 5: old string not found in loop.py")
        with open(loop_path, 'w') as f:
            f.write(original)
        patch.finish()
        sys.exit(1)
else:
    content = content.replace(old5, new5, 1)
    patch.logger.log("  ✓ edit 5: added idle_tasks_registered to get_state()")

# Write modified file
with open(loop_path, 'w') as f:
    f.write(content)

# Syntax check
import py_compile
try:
    py_compile.compile(loop_path, doraise=True)
    patch.logger.log("  ✓ loop.py syntax check passed")
except py_compile.PyCompileError as e:
    patch.errors.append(f"loop.py syntax check failed: {e}")
    patch.logger.log(f"  ✗ loop.py syntax check FAILED — rolling back")
    with open(loop_path, 'w') as f:
        f.write(original)
    patch.finish()
    sys.exit(1)

patch.files_deployed.append(loop_path)

patch.finish()
