#!/usr/bin/env python3
"""
Iris Handler - Telegram interface to Iris consciousness system

Commands:
- /iris - Iris status and quick actions
- /iris_task <goal> - Queue a task for Iris to work on
- /iris_run <code> - Run code directly in sandbox (for testing)
- /iris_test - Run a simple test to verify agency is working
"""

import os
import logging
import httpx
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Iris API endpoint
IRIS_HOST = os.getenv('IRIS_HOST', 'http://localhost:8100')

# Timeout for API calls
IRIS_TIMEOUT = 10.0

# Timeout for task execution (longer)
IRIS_TASK_TIMEOUT = 120.0


async def get_iris_status() -> dict:
    """Fetch current Iris status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{IRIS_HOST}/status",
                timeout=IRIS_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
    except httpx.TimeoutException:
        return {"error": "Iris not responding (timeout)"}
    except httpx.ConnectError:
        return {"error": "Cannot connect to Iris"}
    except Exception as e:
        return {"error": str(e)}


async def run_iris_test() -> dict:
    """Run a simple test task via Iris agency"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{IRIS_HOST}/test_agency",
                timeout=IRIS_TASK_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}", "body": response.text}
    except httpx.TimeoutException:
        return {"error": "Test timed out (this may be normal for long tasks)"}
    except httpx.ConnectError:
        return {"error": "Cannot connect to Iris"}
    except Exception as e:
        return {"error": str(e)}


async def run_iris_code(code: str) -> dict:
    """Run arbitrary code in Iris sandbox"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{IRIS_HOST}/run_code",
                json={"code": code},
                timeout=IRIS_TASK_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}", "body": response.text}
    except httpx.TimeoutException:
        return {"error": "Execution timed out"}
    except httpx.ConnectError:
        return {"error": "Cannot connect to Iris"}
    except Exception as e:
        return {"error": str(e)}


async def queue_iris_task(goal: str, name: str = None) -> dict:
    """Queue a task for Iris to work on"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{IRIS_HOST}/task",
                json={
                    "goal": goal,
                    "name": name or f"telegram_task_{datetime.now().strftime('%H%M%S')}"
                },
                timeout=IRIS_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}", "body": response.text}
    except Exception as e:
        return {"error": str(e)}


def format_mode(mode: str) -> str:
    """Format mode with emoji"""
    mode_emoji = {
        "presence": "🟢",
        "available": "🟡", 
        "background": "🔵",
        "reflection": "🌙"
    }
    return f"{mode_emoji.get(mode, '⚪')} {mode}"


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable form"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h"
    else:
        return f"{seconds/86400:.1f}d"


async def iris_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /iris command - show status and quick actions"""
    status = await get_iris_status()
    
    if "error" in status:
        await update.message.reply_text(
            f"⚠️ **Iris Status: OFFLINE**\n\n"
            f"Error: {status['error']}\n\n"
            f"Try: `docker logs iris-core`",
            parse_mode='Markdown'
        )
        return
    
    mode = format_mode(status.get('mode', 'unknown'))
    uptime = format_uptime(status.get('uptime_seconds', 0))
    cycles = status.get('cycle_count', 0)
    tasks_done = status.get('tasks_completed', 0)
    tasks_failed = status.get('tasks_failed', 0)
    current_task = status.get('current_task')
    
    msg = f"""🔮 **Iris Status**

**Mode:** {mode}
**Uptime:** {uptime}
**Cycles:** {cycles}
**Tasks:** ✅ {tasks_done} / ❌ {tasks_failed}
"""
    
    if current_task:
        msg += f"**Working on:** {current_task}\n"
    
    msg += """
━━━━━━━━━━━━━━━━━━━━━━━━
**Commands:**
`/iris_test` - Test sandbox execution
`/iris_run <code>` - Run Python code
`/iris_task <goal>` - Queue a task
"""
    
    await update.message.reply_text(msg, parse_mode='Markdown')


async def iris_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /iris_test command - run a simple test"""
    await update.message.reply_text("🧪 Running sandbox test...")
    
    result = await run_iris_test()
    
    if "error" in result:
        await update.message.reply_text(
            f"❌ **Test Failed**\n\n"
            f"Error: {result['error']}\n"
            f"{result.get('body', '')}",
            parse_mode='Markdown'
        )
        return
    
    success = result.get('success', False)
    output = result.get('output', '')[:1000]  # Truncate long output
    duration = result.get('duration', 0)
    
    if success:
        await update.message.reply_text(
            f"✅ **Test Passed** ({duration:.2f}s)\n\n"
            f"```\n{output}\n```",
            parse_mode='Markdown'
        )
    else:
        error = result.get('error', 'Unknown error')
        await update.message.reply_text(
            f"❌ **Test Failed** ({duration:.2f}s)\n\n"
            f"Error: {error}\n\n"
            f"```\n{output}\n```",
            parse_mode='Markdown'
        )


async def iris_run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /iris_run <code> command - run arbitrary code"""
    if not context.args:
        await update.message.reply_text(
            "Usage: `/iris_run <python code>`\n\n"
            "Example: `/iris_run print('Hello from Iris!')`\n\n"
            "For multiline, use semicolons:\n"
            "`/iris_run x = 5; print(x * 2)`",
            parse_mode='Markdown'
        )
        return
    
    code = ' '.join(context.args)
    
    # Handle semicolons as newlines for simple multiline
    code = code.replace('; ', '\n').replace(';', '\n')
    
    await update.message.reply_text(f"⚡ Running code...\n```python\n{code}\n```", parse_mode='Markdown')
    
    result = await run_iris_code(code)
    
    if "error" in result and "body" not in result:
        await update.message.reply_text(
            f"❌ **Execution Error**\n\n{result['error']}",
            parse_mode='Markdown'
        )
        return
    
    success = result.get('success', False)
    stdout = result.get('stdout', '')[:1500]
    stderr = result.get('stderr', '')[:500]
    duration = result.get('duration', 0)
    
    if success:
        msg = f"✅ **Success** ({duration:.2f}s)\n"
        if stdout:
            msg += f"```\n{stdout}\n```"
        else:
            msg += "(no output)"
    else:
        msg = f"❌ **Failed** ({duration:.2f}s)\n"
        if stderr:
            msg += f"```\n{stderr}\n```"
        if stdout:
            msg += f"\nStdout:\n```\n{stdout}\n```"
    
    await update.message.reply_text(msg, parse_mode='Markdown')


async def iris_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /iris_task <goal> command - queue a task"""
    if not context.args:
        await update.message.reply_text(
            "Usage: `/iris_task <goal description>`\n\n"
            "Example: `/iris_task Write a script that counts files in /iris/workshop`\n\n"
            "Iris will generate code, test it, and iterate until it works.",
            parse_mode='Markdown'
        )
        return
    
    goal = ' '.join(context.args)
    
    await update.message.reply_text(
        f"📋 Queuing task for Iris...\n\n"
        f"**Goal:** {goal}",
        parse_mode='Markdown'
    )
    
    result = await queue_iris_task(goal)
    
    if "error" in result:
        await update.message.reply_text(
            f"❌ **Failed to queue task**\n\n{result['error']}",
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text(
        f"✅ **Task Queued**\n\n"
        f"Iris will work on this during reflection mode.\n"
        f"Check progress with `/iris`",
        parse_mode='Markdown'
    )
