"""
Test Runner

Execute test suites against models and store results.

Example:
    runner = TestRunner()
    run = await runner.run_suite(
        suite_id="suite_abc",
        model_name="qwen2.5:32b"
    )
    print(f"Accuracy: {run.get_statistics()['accuracy']:.1%}")
"""

from typing import Optional, Dict, Any, Callable
import asyncio
import time
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from utils import generate_id, safe_json_dumps, safe_json_loads
from models.ollama_client import OllamaClient
from models.model_registry import ModelRegistry
from bench.test_loader import TestLoader
from bench.test_suite import TestSuite
from bench.grader import Grader
from bench.test_run import TestRun

logger = logging.getLogger(__name__)


class TestRunner:
    """
    Execute test suites against models.
    
    Coordinates loading tests, generating responses,
    grading answers, and storing results.
    """
    
    def __init__(self):
        """Initialize test runner."""
        self.loader = TestLoader()
        self.grader = Grader()
        self.registry = ModelRegistry()
    
    async def run_suite(
        self,
        suite: Optional[TestSuite] = None,
        suite_id: Optional[str] = None,
        model_name: Optional[str] = None,
        model_id: Optional[str] = None,
        model_params: Optional[Dict] = None,
        progress_callback: Optional[Callable] = None,
        save_to_db: bool = True
    ) -> TestRun:
        """
        Run a test suite against a model.
        
        Args:
            suite: TestSuite to run (or load via suite_id)
            suite_id: Suite ID to load from database
            model_name: Model name to use (e.g., "qwen2.5:32b")
            model_id: Model ID (auto-determined if not provided)
            model_params: Model parameters (temperature, etc.)
            progress_callback: Optional callback(current, total, question_id)
            save_to_db: Whether to save results to database
            
        Returns:
            TestRun with results
            
        Example:
            # From suite object
            run = await runner.run_suite(suite=my_suite, model_name="qwen2.5:32b")
            
            # From database
            run = await runner.run_suite(suite_id="suite_abc", model_name="llama3.1:70b")
            
            # With progress tracking
            def progress(current, total, qid):
                print(f"{current}/{total}: {qid}")
            
            run = await runner.run_suite(
                suite_id="suite_abc",
                model_name="qwen2.5:32b",
                progress_callback=progress
            )
        """
        # Load suite if needed
        if suite is None and suite_id:
            logger.info(f"Loading suite {suite_id}")
            suite = await self.loader.load_from_database(suite_id)
        elif suite is None:
            raise ValueError("Must provide either suite or suite_id")
        
        # Determine model_id
        if model_id is None and model_name:
            model_id = ModelRegistry.normalize_model_id(model_name)
        elif model_id is None:
            raise ValueError("Must provide either model_name or model_id")
        
        # Default model params
        if model_params is None:
            model_params = {}
        
        # Create run
        run_id = generate_id("run")
        run = TestRun(
            run_id=run_id,
            suite_id=suite.suite_id,
            model_id=model_id,
            model_params=model_params
        )
        
        logger.info(f"Starting test run {run_id}: suite={suite.suite_id}, model={model_id}")
        run.start()
        
        try:
            # Save run to database (as "running")
            if save_to_db:
                await self._save_run_to_db(run)
            
            # Execute each question
            total = len(suite.questions)
            
            async with OllamaClient() as client:
                for i, question in enumerate(suite.questions, 1):
                    # Progress callback
                    if progress_callback:
                        progress_callback(i, total, question.question_id)
                    
                    logger.info(f"Question {i}/{total}: {question.question_id}")
                    
                    try:
                        # Generate response
                        start_time = time.time()
                        
                        response = await client.generate(
                            model=model_name,
                            prompt=question.text,
                            **model_params
                        )
                        
                        response_time = time.time() - start_time
                        model_answer = response.get("response", "")
                        
                        # Grade response
                        grading_result = self.grader.grade(
                            model_answer=model_answer,
                            correct_answer=question.correct_answer,
                            answer_type=question.answer_type,
                            grading_criteria=question.grading_criteria
                        )
                        
                        # Add result
                        run.add_result(
                            question_id=question.question_id,
                            model_response=model_answer,
                            grading_result=grading_result,
                            response_time=response_time
                        )
                        
                        # Save individual result to DB
                        if save_to_db:
                            await self._save_result_to_db(run_id, question, model_answer, grading_result, response_time)
                        
                        logger.info(f"  Result: {'✓' if grading_result.is_correct else '✗'} (score={grading_result.score:.2f}, time={response_time:.2f}s)")
                    
                    except Exception as e:
                        logger.error(f"  Error on question {question.question_id}: {e}")
                        # Continue with next question
                        continue
            
            # Mark as completed
            run.complete()
            
            # Update run in database
            if save_to_db:
                await self._update_run_in_db(run)
            
            # Update model's last_used
            await self.registry.update_last_used(model_id)
            
            stats = run.get_statistics()
            logger.info(f"Run {run_id} complete: {stats['correct_answers']}/{stats['total_questions']} correct ({stats['accuracy']:.1%})")
            
            return run
        
        except Exception as e:
            logger.error(f"Run {run_id} failed: {e}")
            run.fail(str(e))
            
            if save_to_db:
                await self._update_run_in_db(run)
            
            raise
    
    async def _save_run_to_db(self, run: TestRun):
        """Save test run to database."""
        model_params_json = safe_json_dumps(run.model_params)
        
        await db.execute("""
            INSERT INTO orch_test_runs (
                run_id, suite_id, model_id, model_params,
                started_at, status, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, run.run_id, run.suite_id, run.model_id, model_params_json,
             run.started_at, run.status, run.started_at)
    
    async def _update_run_in_db(self, run: TestRun):
        """Update test run in database."""
        stats = run.get_statistics()
        
        await db.execute("""
            UPDATE orch_test_runs
            SET
                completed_at = $1,
                total_questions = $2,
                correct_answers = $3,
                accuracy = $4,
                avg_response_time = $5,
                status = $6,
                error_message = $7
            WHERE run_id = $8
        """, run.completed_at, stats['total_questions'], stats['correct_answers'],
             stats['accuracy'], stats['avg_response_time'],
             run.status, run.error_message, run.run_id)
    
    async def _save_result_to_db(
        self,
        run_id: str,
        question,
        model_response: str,
        grading_result,
        response_time: float
    ):
        """Save individual result to database."""
        result_id = generate_id("result")
        grading_details_json = safe_json_dumps(grading_result.details)
        
        await db.execute("""
            INSERT INTO orch_test_results (
                result_id, run_id, question_id,
                model_response, is_correct, partial_credit,
                response_time, grading_details, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
        """, result_id, run_id, question.question_id,
             model_response, grading_result.is_correct, grading_result.partial_credit,
             response_time, grading_details_json)
    
    async def get_run(self, run_id: str) -> TestRun:
        """
        Load test run from database.
        
        Args:
            run_id: Run identifier
            
        Returns:
            TestRun with results
        """
        # Get run metadata
        run_row = await db.fetchrow("""
            SELECT * FROM orch_test_runs WHERE run_id = $1
        """, run_id)
        
        if not run_row:
            raise ValueError(f"Run {run_id} not found")
        
        # Create run
        model_params = safe_json_loads(run_row["model_params"], {})
        run = TestRun(
            run_id=run_row["run_id"],
            suite_id=run_row["suite_id"],
            model_id=run_row["model_id"],
            model_params=model_params
        )
        
        run.started_at = run_row["started_at"]
        run.completed_at = run_row["completed_at"]
        run.status = run_row["status"]
        run.error_message = run_row["error_message"]
        
        # Load results
        result_rows = await db.fetch("""
            SELECT * FROM orch_test_results
            WHERE run_id = $1
            ORDER BY created_at
        """, run_id)
        
        for row in result_rows:
            from bench.grading_result import GradingResult
            
            grading_details = safe_json_loads(row["grading_details"], {})
            
            grading_result = GradingResult(
                is_correct=row["is_correct"],
                score=1.0 if row["is_correct"] else 0.0,
                partial_credit=row["partial_credit"] or 0.0,
                explanation="",
                details=grading_details
            )
            
            run.add_result(
                question_id=row["question_id"],
                model_response=row["model_response"],
                grading_result=grading_result,
                response_time=row["response_time"]
            )
        
        return run
    
    async def list_runs(
        self,
        suite_id: Optional[str] = None,
        model_id: Optional[str] = None,
        limit: int = 10
    ) -> list:
        """
        List test runs.
        
        Args:
            suite_id: Filter by suite
            model_id: Filter by model
            limit: Maximum results
            
        Returns:
            List of run metadata dicts
        """
        conditions = []
        params = []
        
        if suite_id:
            conditions.append(f"suite_id = ${len(params) + 1}")
            params.append(suite_id)
        
        if model_id:
            conditions.append(f"model_id = ${len(params) + 1}")
            params.append(model_id)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        params.append(limit)
        
        rows = await db.fetch(f"""
            SELECT
                run_id, suite_id, model_id,
                started_at, completed_at,
                total_questions, correct_answers, accuracy,
                status
            FROM orch_test_runs
            {where_clause}
            ORDER BY started_at DESC
            LIMIT ${len(params)}
        """, *params)
        
        return [dict(row) for row in rows]
