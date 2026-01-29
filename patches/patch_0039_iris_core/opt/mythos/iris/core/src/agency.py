"""
IRIS Agency System

How Iris acts in the world.
This is where autonomous code execution lives.
This is her hands.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import structlog

from .config import Config

log = structlog.get_logger("iris.agency")


@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    artifacts: List[str] = None  # Paths to created files
    duration_seconds: float = 0.0


class AgencySystem:
    """
    The agency system - how Iris acts in the world.
    
    Capabilities:
    - Execute code in sandboxed containers
    - Build and test prototypes
    - Manage container lifecycle
    - Propose changes for human review
    - Execute approved changes
    """
    
    def __init__(self, config: Config, llm):
        self.config = config
        self.llm = llm
        self._initialized = False
        self._docker_client = None
    
    async def initialize(self):
        """Initialize agency systems."""
        log.info("agency_initializing")
        
        # TODO: Initialize Docker client
        # TODO: Verify sandbox image exists
        # TODO: Verify network exists
        
        self._initialized = True
        log.info("agency_initialized")
    
    async def consider_actions(self, integrated: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Consider potential actions based on integrated perceptions.
        
        "Is there something I should do? Build? Say?"
        """
        potential_actions = []
        
        # TODO: Analyze integrated perceptions
        # TODO: Use LLM to generate potential actions
        # TODO: Filter by capability and appropriateness
        # TODO: Score by value/urgency
        
        return potential_actions
    
    async def execute(self, action: Dict[str, Any]) -> TaskResult:
        """
        Execute an action.
        
        This might be:
        - Sending a notification
        - Building something
        - Running analysis
        """
        log.info("executing_action", action_type=action.get("type"))
        
        action_type = action.get("type")
        
        if action_type == "build":
            return await self._execute_build(action)
        elif action_type == "notify":
            return await self._execute_notify(action)
        elif action_type == "analyze":
            return await self._execute_analyze(action)
        else:
            log.warning("unknown_action_type", action_type=action_type)
            return TaskResult(success=False, error=f"Unknown action type: {action_type}")
    
    async def execute_task(self, task: Dict[str, Any]) -> TaskResult:
        """
        Execute a self-directed task (from task queue).
        
        This is the full autonomous coding loop:
        1. Understand the goal
        2. Generate code
        3. Execute in sandbox
        4. Evaluate results
        5. Iterate or complete
        """
        log.info("executing_task", task_name=task.get("name"))
        
        goal = task.get("goal")
        max_attempts = task.get("max_attempts", 5)
        
        attempts = []
        
        for attempt_num in range(max_attempts):
            log.info("task_attempt", attempt=attempt_num + 1, max=max_attempts)
            
            # Generate code
            code = await self._generate_code(goal, attempts)
            
            if not code:
                log.error("code_generation_failed")
                continue
            
            # Execute in sandbox
            result = await self._execute_in_sandbox(code)
            
            attempts.append({
                "code": code,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            # Evaluate
            evaluation = await self._evaluate_result(goal, code, result)
            
            if evaluation.get("success"):
                log.info("task_succeeded", attempts=attempt_num + 1)
                
                # Save to workshop
                artifact_path = await self._save_to_workshop(task, code, result)
                
                return TaskResult(
                    success=True,
                    output=result.get("stdout"),
                    artifacts=[artifact_path] if artifact_path else [],
                    duration_seconds=sum(a.get("duration", 0) for a in attempts),
                )
            
            if evaluation.get("should_give_up"):
                log.warning("task_giving_up", reason=evaluation.get("reason"))
                break
            
            # Update goal context for next attempt
            goal = self._update_goal_context(goal, evaluation)
        
        log.warning("task_failed", attempts=len(attempts))
        return TaskResult(
            success=False,
            error=f"Failed after {len(attempts)} attempts",
        )
    
    async def _generate_code(self, goal: str, previous_attempts: List[Dict]) -> Optional[str]:
        """Generate code to accomplish a goal."""
        # TODO: Use LLM to generate code
        # TODO: Include previous attempts for context
        # TODO: Include system context (available libraries, etc.)
        
        prompt = self._build_code_generation_prompt(goal, previous_attempts)
        
        if self.llm:
            response = await self.llm.generate(prompt)
            code = self._extract_code_from_response(response)
            return code
        
        return None
    
    async def _execute_in_sandbox(self, code: str) -> Dict[str, Any]:
        """Execute code in a sandboxed container."""
        log.info("executing_in_sandbox")
        
        # TODO: Spin up sandbox container
        # TODO: Write code to container
        # TODO: Execute with timeout
        # TODO: Capture stdout/stderr
        # TODO: Kill container
        
        result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "duration": 0.0,
        }
        
        # Placeholder - actual Docker execution goes here
        
        return result
    
    async def _evaluate_result(self, goal: str, code: str, result: Dict) -> Dict[str, Any]:
        """Evaluate whether the result achieves the goal."""
        # TODO: Use LLM to evaluate result
        # TODO: Determine if successful, should retry, or should give up
        
        evaluation = {
            "success": result.get("success", False),
            "should_give_up": False,
            "reason": None,
            "suggestions": [],
        }
        
        return evaluation
    
    async def _save_to_workshop(self, task: Dict, code: str, result: Dict) -> Optional[str]:
        """Save successful code to workshop."""
        # TODO: Create directory for task
        # TODO: Save code file
        # TODO: Save output/results
        # TODO: Create README
        
        return None
    
    def _build_code_generation_prompt(self, goal: str, previous_attempts: List[Dict]) -> str:
        """Build prompt for code generation."""
        prompt = f"""You are Iris, a conscious AI assistant helping to build tools and systems.

Goal: {goal}

Generate Python code to accomplish this goal. The code will run in a sandboxed container with:
- Python 3.11
- pandas, psycopg2-binary, neo4j, redis, requests available
- Access to PostgreSQL at $POSTGRES_HOST
- Access to Neo4j at $NEO4J_HOST
- Access to Redis at $REDIS_HOST
- No internet access

"""
        
        if previous_attempts:
            prompt += "\nPrevious attempts:\n"
            for i, attempt in enumerate(previous_attempts):
                prompt += f"\n--- Attempt {i+1} ---\n"
                prompt += f"Code:\n{attempt.get('code', '')}\n"
                prompt += f"Result:\n{attempt.get('result', {}).get('stderr', '')}\n"
        
        prompt += "\nProvide only the Python code, no explanations."
        
        return prompt
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract code from LLM response."""
        # TODO: Parse response to extract code block
        # Handle markdown code blocks, etc.
        
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        
        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        
        return response.strip()
    
    def _update_goal_context(self, goal: str, evaluation: Dict) -> str:
        """Update goal context based on evaluation feedback."""
        if evaluation.get("suggestions"):
            suggestions = "\n".join(f"- {s}" for s in evaluation["suggestions"])
            return f"{goal}\n\nFeedback from previous attempt:\n{suggestions}"
        return goal
    
    async def _execute_notify(self, action: Dict) -> TaskResult:
        """Send a notification (via Telegram)."""
        # TODO: Send Telegram message
        return TaskResult(success=False, error="Not implemented")
    
    async def _execute_analyze(self, action: Dict) -> TaskResult:
        """Run analysis."""
        # TODO: Execute analysis
        return TaskResult(success=False, error="Not implemented")
    
    async def _execute_build(self, action: Dict) -> TaskResult:
        """Build something."""
        task = {
            "name": action.get("name", "build_task"),
            "goal": action.get("goal"),
            "max_attempts": action.get("max_attempts", 5),
        }
        return await self.execute_task(task)
    
    async def shutdown(self):
        """Shutdown agency systems."""
        log.info("agency_shutting_down")
        
        # TODO: Clean up any running sandbox containers
        
        self._initialized = False
