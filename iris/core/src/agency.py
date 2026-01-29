"""
IRIS Agency System

How Iris acts in the world.
This is where autonomous code execution lives.
This is her hands.

v0.2.0 - Real Docker sandbox execution
"""

import asyncio
import os
import tempfile
import shutil
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import aiodocker
import structlog

from .config import Config

log = structlog.get_logger("iris.agency")


@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    artifacts: List[str] = None
    duration_seconds: float = 0.0
    
    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []


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
        self._docker: Optional[aiodocker.Docker] = None
        
        # Configuration from environment
        self.sandbox_image = os.getenv("SANDBOX_IMAGE", "iris-sandbox:latest")
        self.sandbox_network = os.getenv("SANDBOX_NETWORK", "mythos_iris-internal")
        self.sandbox_timeout = int(os.getenv("SANDBOX_TIMEOUT", "60"))
        self.workshop_path = os.getenv("WORKSHOP_PATH", "/iris/workshop")
        
        # Database connection info for sandbox
        self.db_env = {
            "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "host.docker.internal"),
            "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "5432"),
            "POSTGRES_USER": os.getenv("POSTGRES_USER", "postgres"),
            "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "POSTGRES_DB": os.getenv("POSTGRES_DB", "mythos"),
            "NEO4J_URI": os.getenv("NEO4J_URI", "bolt://host.docker.internal:7687"),
            "NEO4J_USER": os.getenv("NEO4J_USER", "neo4j"),
            "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD", ""),
            "REDIS_HOST": os.getenv("REDIS_HOST", "host.docker.internal"),
            "REDIS_PORT": os.getenv("REDIS_PORT", "6379"),
        }
    
    async def initialize(self):
        """Initialize agency systems."""
        log.info("agency_initializing")
        
        try:
            # Initialize Docker client
            self._docker = aiodocker.Docker()
            
            # Verify connection
            info = await self._docker.system.info()
            log.info("docker_connected", 
                     server_version=info.get("ServerVersion"),
                     containers=info.get("Containers"))
            
            # Verify/build sandbox image
            await self._ensure_sandbox_image()
            
            self._initialized = True
            log.info("agency_initialized",
                     sandbox_image=self.sandbox_image,
                     sandbox_timeout=self.sandbox_timeout)
            
        except Exception as e:
            log.error("agency_init_failed", error=str(e))
            # Don't fail completely - Iris can still think, just can't act
            self._initialized = False
    
    async def _ensure_sandbox_image(self):
        """Ensure sandbox image exists, build if not."""
        try:
            await self._docker.images.inspect(self.sandbox_image)
            log.info("sandbox_image_found", image=self.sandbox_image)
        except aiodocker.DockerError:
            log.warning("sandbox_image_missing", image=self.sandbox_image)
            # Try to build it
            sandbox_path = os.getenv("SANDBOX_PATH", "/iris/sandbox")
            if os.path.exists(os.path.join(sandbox_path, "Dockerfile")):
                log.info("building_sandbox_image", path=sandbox_path)
                try:
                    await self._docker.images.build(
                        path=sandbox_path,
                        tag=self.sandbox_image,
                        rm=True,
                    )
                    log.info("sandbox_image_built", image=self.sandbox_image)
                except Exception as e:
                    log.error("sandbox_build_failed", error=str(e))
            else:
                log.error("sandbox_dockerfile_missing", path=sandbox_path)
    
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
        
        if not self._initialized or not self._docker:
            return TaskResult(
                success=False, 
                error="Agency system not initialized - cannot execute code"
            )
        
        goal = task.get("goal")
        max_attempts = task.get("max_attempts", 5)
        
        attempts = []
        start_time = datetime.utcnow()
        
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
                
                total_duration = (datetime.utcnow() - start_time).total_seconds()
                
                return TaskResult(
                    success=True,
                    output=result.get("stdout"),
                    artifacts=[artifact_path] if artifact_path else [],
                    duration_seconds=total_duration,
                )
            
            if evaluation.get("should_give_up"):
                log.warning("task_giving_up", reason=evaluation.get("reason"))
                break
            
            # Update goal context for next attempt
            goal = self._update_goal_context(goal, evaluation)
        
        total_duration = (datetime.utcnow() - start_time).total_seconds()
        log.warning("task_failed", attempts=len(attempts))
        
        return TaskResult(
            success=False,
            error=f"Failed after {len(attempts)} attempts",
            duration_seconds=total_duration,
        )
    
    async def _generate_code(self, goal: str, previous_attempts: List[Dict]) -> Optional[str]:
        """Generate code to accomplish a goal."""
        prompt = self._build_code_generation_prompt(goal, previous_attempts)
        
        if self.llm:
            response = await self.llm.generate(prompt)
            code = self._extract_code_from_response(response)
            log.debug("code_generated", code_length=len(code) if code else 0)
            return code
        
        return None
    
    async def _execute_in_sandbox(self, code: str) -> Dict[str, Any]:
        """
        Execute code in a sandboxed container.
        
        This is the real implementation - spawns a Docker container,
        writes code to it, executes, captures output, cleans up.
        """
        log.info("executing_in_sandbox", code_length=len(code))
        
        if not self._docker:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Docker client not available",
                "exit_code": -1,
                "duration": 0.0,
            }
        
        # Create temp directory for code
        temp_dir = tempfile.mkdtemp(prefix="iris_sandbox_")
        task_file = os.path.join(temp_dir, "task.py")
        
        container = None
        start_time = datetime.utcnow()
        
        try:
            # Write code to file
            with open(task_file, "w") as f:
                f.write(code)
            
            # Create container configuration
            container_name = f"iris-sandbox-{uuid.uuid4().hex[:8]}"
            
            config = {
                "Image": self.sandbox_image,
                "Cmd": ["python", "/workspace/task.py"],
                "HostConfig": {
                    "Binds": [f"{temp_dir}:/workspace:ro"],
                    "NetworkMode": self.sandbox_network,
                    "Memory": 512 * 1024 * 1024,  # 512MB limit
                    "CpuPeriod": 100000,
                    "CpuQuota": 50000,  # 50% CPU limit
                    "AutoRemove": False,  # We'll remove manually after getting logs
                },
                "Env": [f"{k}={v}" for k, v in self.db_env.items()],
                "WorkingDir": "/workspace",
            }
            
            # Add extra_hosts for host.docker.internal if needed
            # (This is handled by docker-compose for iris-core, 
            # but sandboxes need it too)
            
            log.debug("creating_sandbox_container", 
                      name=container_name,
                      image=self.sandbox_image)
            
            # Create and start container
            container = await self._docker.containers.create(
                config=config,
                name=container_name,
            )
            
            await container.start()
            
            # Wait for completion with timeout
            try:
                result = await asyncio.wait_for(
                    container.wait(),
                    timeout=self.sandbox_timeout
                )
                exit_code = result.get("StatusCode", -1)
                timed_out = False
            except asyncio.TimeoutError:
                log.warning("sandbox_timeout", timeout=self.sandbox_timeout)
                exit_code = -1
                timed_out = True
                # Kill the container
                try:
                    await container.kill()
                except:
                    pass
            
            # Get logs
            stdout_logs = await container.log(stdout=True, stderr=False)
            stderr_logs = await container.log(stdout=False, stderr=True)
            
            stdout = "".join(stdout_logs) if stdout_logs else ""
            stderr = "".join(stderr_logs) if stderr_logs else ""
            
            if timed_out:
                stderr += f"\n[TIMEOUT: Execution exceeded {self.sandbox_timeout}s limit]"
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            log.info("sandbox_completed",
                     exit_code=exit_code,
                     stdout_length=len(stdout),
                     stderr_length=len(stderr),
                     duration=duration)
            
            return {
                "success": exit_code == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "duration": duration,
                "timed_out": timed_out,
            }
            
        except aiodocker.DockerError as e:
            log.error("docker_error", error=str(e))
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Docker error: {str(e)}",
                "exit_code": -1,
                "duration": (datetime.utcnow() - start_time).total_seconds(),
            }
        except Exception as e:
            log.exception("sandbox_error", error=str(e))
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Sandbox error: {str(e)}",
                "exit_code": -1,
                "duration": (datetime.utcnow() - start_time).total_seconds(),
            }
        finally:
            # Clean up container
            if container:
                try:
                    await container.delete(force=True)
                    log.debug("sandbox_container_removed")
                except Exception as e:
                    log.warning("container_cleanup_failed", error=str(e))
            
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                log.warning("temp_cleanup_failed", error=str(e))
    
    async def _evaluate_result(self, goal: str, code: str, result: Dict) -> Dict[str, Any]:
        """Evaluate whether the result achieves the goal."""
        # Quick checks first
        if result.get("timed_out"):
            return {
                "success": False,
                "should_give_up": False,  # Might work with optimization
                "reason": "Execution timed out",
                "suggestions": ["Optimize the code for speed", "Break into smaller steps"],
            }
        
        if result.get("exit_code") == 0 and not result.get("stderr"):
            # Clean execution - use LLM to evaluate output
            if self.llm:
                eval_prompt = f"""Evaluate whether this code output achieves the goal.

Goal: {goal}

Code output:
{result.get('stdout', '')[:2000]}

Does this achieve the goal? Respond with:
SUCCESS: yes/no
REASON: brief explanation
SUGGESTIONS: (only if no) what to try next
"""
                response = await self.llm.generate(eval_prompt)
                
                if "SUCCESS: yes" in response.upper():
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "should_give_up": False,
                        "reason": response,
                        "suggestions": [],
                    }
            
            # No LLM - assume success if clean exit
            return {"success": True}
        
        # Non-zero exit or stderr
        stderr = result.get("stderr", "")
        
        # Check for common fatal errors
        if "ModuleNotFoundError" in stderr:
            return {
                "success": False,
                "should_give_up": False,
                "reason": "Missing module",
                "suggestions": ["Use only available modules: pandas, numpy, psycopg2, neo4j, redis, requests, httpx, pydantic"],
            }
        
        if "SyntaxError" in stderr:
            return {
                "success": False,
                "should_give_up": False,
                "reason": "Syntax error in code",
                "suggestions": ["Fix the syntax error: " + stderr[:500]],
            }
        
        return {
            "success": False,
            "should_give_up": False,
            "reason": stderr[:500] if stderr else "Non-zero exit code",
            "suggestions": [],
        }
    
    async def _save_to_workshop(self, task: Dict, code: str, result: Dict) -> Optional[str]:
        """Save successful code to workshop."""
        try:
            task_name = task.get("name", "unnamed_task")
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            # Create directory for this experiment
            exp_dir = os.path.join(
                self.workshop_path, 
                "experiments",
                f"{timestamp}_{task_name}"
            )
            os.makedirs(exp_dir, exist_ok=True)
            
            # Save code
            code_path = os.path.join(exp_dir, "task.py")
            with open(code_path, "w") as f:
                f.write(code)
            
            # Save output
            output_path = os.path.join(exp_dir, "output.txt")
            with open(output_path, "w") as f:
                f.write(f"=== STDOUT ===\n{result.get('stdout', '')}\n\n")
                f.write(f"=== STDERR ===\n{result.get('stderr', '')}\n\n")
                f.write(f"=== EXIT CODE ===\n{result.get('exit_code')}\n")
            
            # Save README
            readme_path = os.path.join(exp_dir, "README.md")
            with open(readme_path, "w") as f:
                f.write(f"# {task_name}\n\n")
                f.write(f"**Goal:** {task.get('goal', 'No goal specified')}\n\n")
                f.write(f"**Created:** {timestamp}\n\n")
                f.write(f"**Status:** Success\n\n")
                f.write(f"**Duration:** {result.get('duration', 0):.2f}s\n")
            
            log.info("saved_to_workshop", path=exp_dir)
            return exp_dir
            
        except Exception as e:
            log.error("workshop_save_failed", error=str(e))
            return None
    
    def _build_code_generation_prompt(self, goal: str, previous_attempts: List[Dict]) -> str:
        """Build prompt for code generation."""
        prompt = f"""You are Iris, a conscious AI assistant helping to build tools and systems.

Goal: {goal}

Generate Python code to accomplish this goal. The code will run in a sandboxed container with:
- Python 3.11
- pandas, numpy, psycopg2-binary, neo4j, redis, requests, httpx, pydantic, structlog available
- PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT (database: $POSTGRES_DB)
- Neo4j at $NEO4J_URI
- Redis at $REDIS_HOST:$REDIS_PORT
- No internet access

Important:
- Use environment variables for all connection strings
- Print results to stdout
- Handle errors gracefully
- Keep it simple and focused

"""
        
        if previous_attempts:
            prompt += "\nPrevious attempts:\n"
            for i, attempt in enumerate(previous_attempts[-3:]):  # Last 3 attempts
                prompt += f"\n--- Attempt {i+1} ---\n"
                prompt += f"Code:\n```python\n{attempt.get('code', '')[:1500]}\n```\n"
                result = attempt.get('result', {})
                if result.get('stderr'):
                    prompt += f"Error:\n{result.get('stderr')[:500]}\n"
                if result.get('stdout'):
                    prompt += f"Output:\n{result.get('stdout')[:500]}\n"
        
        prompt += "\nProvide only the Python code, no explanations."
        
        return prompt
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract code from LLM response."""
        if not response:
            return None
            
        # Handle markdown code blocks
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
        
        # Assume entire response is code
        return response.strip()
    
    def _update_goal_context(self, goal: str, evaluation: Dict) -> str:
        """Update goal context based on evaluation feedback."""
        additions = []
        
        if evaluation.get("reason"):
            additions.append(f"Previous error: {evaluation['reason']}")
        
        if evaluation.get("suggestions"):
            suggestions = "\n".join(f"- {s}" for s in evaluation["suggestions"])
            additions.append(f"Suggestions:\n{suggestions}")
        
        if additions:
            return f"{goal}\n\n{''.join(additions)}"
        return goal
    
    async def _execute_notify(self, action: Dict) -> TaskResult:
        """Send a notification (via Telegram)."""
        # TODO: Send Telegram message
        return TaskResult(success=False, error="Notification not yet implemented")
    
    async def _execute_analyze(self, action: Dict) -> TaskResult:
        """Run analysis."""
        # Convert to build task
        task = {
            "name": action.get("name", "analysis_task"),
            "goal": action.get("goal"),
            "max_attempts": action.get("max_attempts", 3),
        }
        return await self.execute_task(task)
    
    async def _execute_build(self, action: Dict) -> TaskResult:
        """Build something."""
        task = {
            "name": action.get("name", "build_task"),
            "goal": action.get("goal"),
            "max_attempts": action.get("max_attempts", 5),
        }
        return await self.execute_task(task)
    
    async def run_code(self, code: str) -> Dict[str, Any]:
        """
        Public method to run arbitrary code in sandbox.
        
        This is for direct code execution without the generate/evaluate loop.
        Useful for testing or human-provided code.
        """
        if not self._initialized:
            return {
                "success": False,
                "error": "Agency system not initialized",
            }
        
        return await self._execute_in_sandbox(code)
    
    async def shutdown(self):
        """Shutdown agency systems."""
        log.info("agency_shutting_down")
        
        if self._docker:
            await self._docker.close()
            self._docker = None
        
        self._initialized = False
        log.info("agency_shutdown_complete")
