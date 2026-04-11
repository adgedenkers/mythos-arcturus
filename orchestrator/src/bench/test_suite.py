"""
Test Suite

Collection of related test questions.

Example:
    suite = TestSuite(
        name="Math Basics",
        category="math",
        description="Basic arithmetic questions"
    )
    suite.add_question(question1)
    suite.add_question(question2)
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import generate_id
from bench.test_question import TestQuestion


class TestSuite:
    """
    Collection of test questions for a specific category.
    
    Organizes related questions into a testable suite with
    metadata and statistics.
    """
    
    def __init__(
        self,
        name: str,
        category: str,
        description: Optional[str] = None,
        suite_id: Optional[str] = None,
        version: str = "1.0",
        public: bool = True,
        created_by: Optional[str] = None
    ):
        """
        Initialize a test suite.
        
        Args:
            name: Suite name
            category: Category (math, code, dates, etc.)
            description: Optional description
            suite_id: Unique identifier (auto-generated if None)
            version: Suite version
            public: Whether suite is public
            created_by: Creator identifier
        """
        self.suite_id = suite_id or generate_id("suite")
        self.name = name
        self.category = category
        self.description = description
        self.version = version
        self.public = public
        self.created_by = created_by
        self.questions: List[TestQuestion] = []
        self.created_at = datetime.now()
    
    def add_question(self, question: TestQuestion) -> None:
        """
        Add a question to the suite.
        
        Args:
            question: TestQuestion to add
        """
        # Validate question first
        is_valid, error = question.validate()
        if not is_valid:
            raise ValueError(f"Invalid question: {error}")
        
        self.questions.append(question)
    
    def remove_question(self, question_id: str) -> bool:
        """
        Remove a question by ID.
        
        Args:
            question_id: ID of question to remove
            
        Returns:
            True if removed, False if not found
        """
        for i, q in enumerate(self.questions):
            if q.question_id == question_id:
                self.questions.pop(i)
                return True
        return False
    
    def get_question(self, question_id: str) -> Optional[TestQuestion]:
        """
        Get a question by ID.
        
        Args:
            question_id: Question identifier
            
        Returns:
            TestQuestion or None
        """
        for q in self.questions:
            if q.question_id == question_id:
                return q
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get suite statistics.
        
        Returns:
            Dictionary with stats
        """
        if not self.questions:
            return {
                "total_questions": 0,
                "difficulty_distribution": {},
                "answer_type_distribution": {},
                "tags": []
            }
        
        # Count by difficulty
        difficulty_dist = {}
        for q in self.questions:
            if q.difficulty:
                difficulty_dist[q.difficulty] = difficulty_dist.get(q.difficulty, 0) + 1
        
        # Count by answer type
        answer_type_dist = {}
        for q in self.questions:
            answer_type_dist[q.answer_type] = answer_type_dist.get(q.answer_type, 0) + 1
        
        # Collect all tags
        all_tags = set()
        for q in self.questions:
            all_tags.update(q.tags)
        
        return {
            "total_questions": len(self.questions),
            "difficulty_distribution": difficulty_dist,
            "answer_type_distribution": answer_type_dist,
            "tags": sorted(list(all_tags))
        }
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate suite data.
        
        Returns:
            (is_valid, error_message)
        """
        if not self.name or not self.name.strip():
            return False, "Suite name cannot be empty"
        
        if not self.category or not self.category.strip():
            return False, "Category cannot be empty"
        
        if not self.questions:
            return False, "Suite must have at least one question"
        
        # Validate all questions
        for i, q in enumerate(self.questions):
            is_valid, error = q.validate()
            if not is_valid:
                return False, f"Question {i+1} invalid: {error}"
        
        return True, None
    
    def to_dict(self, include_questions: bool = True) -> Dict[str, Any]:
        """
        Convert suite to dictionary.
        
        Args:
            include_questions: Whether to include full question data
            
        Returns:
            Dictionary representation
        """
        data = {
            "suite_id": self.suite_id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "version": self.version,
            "public": self.public,
            "created_by": self.created_by,
            "question_count": len(self.questions)
        }
        
        if include_questions:
            data["questions"] = [q.to_dict() for q in self.questions]
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestSuite':
        """
        Create suite from dictionary.
        
        Args:
            data: Dictionary with suite data
            
        Returns:
            TestSuite instance
        """
        suite = cls(
            name=data["name"],
            category=data["category"],
            description=data.get("description"),
            suite_id=data.get("suite_id"),
            version=data.get("version", "1.0"),
            public=data.get("public", True),
            created_by=data.get("created_by")
        )
        
        # Add questions if present
        if "questions" in data:
            for q_data in data["questions"]:
                question = TestQuestion.from_dict(q_data)
                suite.add_question(question)
        
        return suite
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<TestSuite {self.suite_id}: {self.name} ({len(self.questions)} questions)>"
    
    def __len__(self) -> int:
        """Return number of questions."""
        return len(self.questions)
