"""
Grading Result

Result of grading a model's answer against the correct answer.

Example:
    result = GradingResult(
        is_correct=True,
        score=1.0,
        explanation="Exact match"
    )
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class GradingResult:
    """
    Result of grading an answer.
    
    Contains correctness determination, score, and explanation.
    """
    
    is_correct: bool
    score: float  # 0.0 to 1.0
    partial_credit: float = 0.0  # 0.0 to 1.0
    explanation: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate scores are in valid range."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")
        
        if not 0.0 <= self.partial_credit <= 1.0:
            raise ValueError(f"Partial credit must be between 0.0 and 1.0, got {self.partial_credit}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_correct": self.is_correct,
            "score": self.score,
            "partial_credit": self.partial_credit,
            "explanation": self.explanation,
            "details": self.details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GradingResult':
        """Create from dictionary."""
        return cls(
            is_correct=data["is_correct"],
            score=data["score"],
            partial_credit=data.get("partial_credit", 0.0),
            explanation=data.get("explanation", ""),
            details=data.get("details", {})
        )
    
    def __repr__(self) -> str:
        """String representation."""
        status = "✓" if self.is_correct else "✗"
        return f"<GradingResult {status} score={self.score:.2f}>"
