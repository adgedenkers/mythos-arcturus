"""
Test Question

Represents a single test question with grading criteria.

Example:
    question = TestQuestion(
        text="What is 2+2?",
        correct_answer="4",
        answer_type="exact"
    )
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import generate_id, safe_json_dumps, safe_json_loads

class TestQuestion:
    """
    Individual test question with grading criteria.
    
    Represents a single question that can be asked to a model,
    along with the expected answer and grading rules.
    """
    
    def __init__(
        self,
        text: str,
        correct_answer: str,
        answer_type: str = "exact",
        question_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        tags: Optional[List[str]] = None,
        grading_criteria: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Initialize a test question.
        
        Args:
            text: The question text
            correct_answer: The expected correct answer
            answer_type: Type of answer validation
                - "exact": Exact string match
                - "numeric": Numeric comparison
                - "semantic": Semantic similarity
                - "code": Code execution match
            question_id: Unique identifier (auto-generated if None)
            difficulty: Difficulty level (easy, medium, hard, expert)
            tags: List of category tags
            grading_criteria: Additional grading parameters
            metadata: Additional metadata
        """
        self.question_id = question_id or generate_id("q")
        self.text = text
        self.correct_answer = correct_answer
        self.answer_type = answer_type
        self.difficulty = difficulty
        self.tags = tags or []
        self.grading_criteria = grading_criteria or {}
        self.metadata = metadata or {}
        self.created_at = datetime.now()
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate question data.
        
        Returns:
            (is_valid, error_message)
        """
        if not self.text or not self.text.strip():
            return False, "Question text cannot be empty"
        
        if not self.correct_answer:
            return False, "Correct answer cannot be empty"
        
        valid_types = ["exact", "numeric", "semantic", "code"]
        if self.answer_type not in valid_types:
            return False, f"Answer type must be one of: {valid_types}"
        
        if self.difficulty and self.difficulty not in ["easy", "medium", "hard", "expert"]:
            return False, "Difficulty must be: easy, medium, hard, or expert"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert question to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "question_id": self.question_id,
            "text": self.text,
            "correct_answer": self.correct_answer,
            "answer_type": self.answer_type,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "grading_criteria": self.grading_criteria,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestQuestion':
        """
        Create question from dictionary.
        
        Args:
            data: Dictionary with question data
            
        Returns:
            TestQuestion instance
        """
        return cls(
            text=data["text"],
            correct_answer=data["correct_answer"],
            answer_type=data.get("answer_type", "exact"),
            question_id=data.get("question_id"),
            difficulty=data.get("difficulty"),
            tags=data.get("tags", []),
            grading_criteria=data.get("grading_criteria", {}),
            metadata=data.get("metadata", {})
        )
    
    def __repr__(self) -> str:
        """String representation."""
        difficulty_str = f" [{self.difficulty}]" if self.difficulty else ""
        return f"<TestQuestion {self.question_id}{difficulty_str}: {self.text[:50]}...>"
