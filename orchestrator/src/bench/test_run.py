"""
Test Run

Container for test run results and statistics.

Example:
    run = TestRun(run_id="run_123", suite_id="suite_abc")
    run.add_result(question_id, result)
    stats = run.get_statistics()
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from bench.grading_result import GradingResult


@dataclass
class QuestionResult:
    """Result for a single question."""
    question_id: str
    model_response: str
    grading_result: GradingResult
    response_time: float  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "model_response": self.model_response,
            "grading_result": self.grading_result.to_dict(),
            "response_time": self.response_time
        }


class TestRun:
    """
    Container for test run results.
    
    Tracks results for all questions in a test suite run,
    calculates statistics, and manages persistence.
    """
    
    def __init__(
        self,
        run_id: str,
        suite_id: str,
        model_id: str,
        model_params: Optional[Dict] = None
    ):
        """
        Initialize test run.
        
        Args:
            run_id: Unique run identifier
            suite_id: Test suite identifier
            model_id: Model identifier
            model_params: Model parameters used
        """
        self.run_id = run_id
        self.suite_id = suite_id
        self.model_id = model_id
        self.model_params = model_params or {}
        
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.status = "pending"  # pending, running, completed, failed
        self.error_message: Optional[str] = None
        
        self.results: List[QuestionResult] = []
    
    def start(self):
        """Mark run as started."""
        self.started_at = datetime.now()
        self.status = "running"
    
    def complete(self):
        """Mark run as completed."""
        self.completed_at = datetime.now()
        self.status = "completed"
    
    def fail(self, error: str):
        """Mark run as failed."""
        self.completed_at = datetime.now()
        self.status = "failed"
        self.error_message = error
    
    def add_result(
        self,
        question_id: str,
        model_response: str,
        grading_result: GradingResult,
        response_time: float
    ):
        """
        Add a question result.
        
        Args:
            question_id: Question identifier
            model_response: Model's answer
            grading_result: Grading outcome
            response_time: Time to generate response (seconds)
        """
        result = QuestionResult(
            question_id=question_id,
            model_response=model_response,
            grading_result=grading_result,
            response_time=response_time
        )
        self.results.append(result)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate run statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.results:
            return {
                "total_questions": 0,
                "correct_answers": 0,
                "accuracy": 0.0,
                "avg_score": 0.0,
                "avg_response_time": 0.0,
                "total_time": 0.0
            }
        
        total = len(self.results)
        correct = sum(1 for r in self.results if r.grading_result.is_correct)
        total_score = sum(r.grading_result.score for r in self.results)
        total_time = sum(r.response_time for r in self.results)
        
        # Calculate duration
        duration = 0.0
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()
        
        return {
            "total_questions": total,
            "correct_answers": correct,
            "accuracy": correct / total if total > 0 else 0.0,
            "avg_score": total_score / total if total > 0 else 0.0,
            "avg_response_time": total_time / total if total > 0 else 0.0,
            "total_time": duration,
            "status": self.status
        }
    
    def to_dict(self, include_results: bool = True) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Args:
            include_results: Include individual results
            
        Returns:
            Dictionary representation
        """
        stats = self.get_statistics()
        
        data = {
            "run_id": self.run_id,
            "suite_id": self.suite_id,
            "model_id": self.model_id,
            "model_params": self.model_params,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "error_message": self.error_message,
            "statistics": stats
        }
        
        if include_results:
            data["results"] = [r.to_dict() for r in self.results]
        
        return data
    
    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return f"<TestRun {self.run_id}: {stats['correct_answers']}/{stats['total_questions']} correct>"
