"""
Grader

Answer validation and scoring.

Example:
    grader = Grader()
    result = grader.grade(
        model_answer="4",
        correct_answer="4",
        answer_type="exact"
    )
"""

from typing import Optional, Dict, Any
import re
import logging

from bench.grading_result import GradingResult

logger = logging.getLogger(__name__)


class Grader:
    """
    Grade model answers against correct answers.
    
    Supports multiple grading strategies:
    - exact: Exact string match
    - numeric: Numeric comparison with tolerance
    - semantic: Semantic similarity (basic)
    - code: Code execution (basic)
    """
    
    def grade(
        self,
        model_answer: str,
        correct_answer: str,
        answer_type: str = "exact",
        grading_criteria: Optional[Dict] = None
    ) -> GradingResult:
        """
        Grade a model's answer.
        
        Args:
            model_answer: The model's response
            correct_answer: The expected correct answer
            answer_type: Type of grading (exact, numeric, semantic, code)
            grading_criteria: Additional grading parameters
            
        Returns:
            GradingResult
            
        Example:
            result = grader.grade("4", "4", "exact")
            if result.is_correct:
                print("Correct!")
        """
        grading_criteria = grading_criteria or {}
        
        # Route to appropriate grader
        if answer_type == "exact":
            return self.grade_exact(model_answer, correct_answer, grading_criteria)
        elif answer_type == "numeric":
            return self.grade_numeric(model_answer, correct_answer, grading_criteria)
        elif answer_type == "semantic":
            return self.grade_semantic(model_answer, correct_answer, grading_criteria)
        elif answer_type == "code":
            return self.grade_code(model_answer, correct_answer, grading_criteria)
        else:
            raise ValueError(f"Unknown answer type: {answer_type}")
    
    def grade_exact(
        self,
        model_answer: str,
        correct_answer: str,
        criteria: Dict
    ) -> GradingResult:
        """
        Grade using exact string matching.
        
        Criteria options:
        - case_sensitive (bool): Whether to match case (default: True)
        - strip_whitespace (bool): Strip leading/trailing whitespace (default: True)
        - normalize_whitespace (bool): Normalize internal whitespace (default: False)
        
        Args:
            model_answer: Model's response
            correct_answer: Expected answer
            criteria: Grading criteria
            
        Returns:
            GradingResult
        """
        case_sensitive = criteria.get("case_sensitive", True)
        strip_whitespace = criteria.get("strip_whitespace", True)
        normalize_whitespace = criteria.get("normalize_whitespace", False)
        
        # Prepare answers
        model = model_answer
        correct = correct_answer
        
        if strip_whitespace:
            model = model.strip()
            correct = correct.strip()
        
        if normalize_whitespace:
            model = ' '.join(model.split())
            correct = ' '.join(correct.split())
        
        if not case_sensitive:
            model = model.lower()
            correct = correct.lower()
        
        # Compare
        is_correct = model == correct
        
        return GradingResult(
            is_correct=is_correct,
            score=1.0 if is_correct else 0.0,
            explanation="Exact match" if is_correct else "Does not match",
            details={
                "model_answer": model_answer,
                "correct_answer": correct_answer,
                "case_sensitive": case_sensitive
            }
        )
    
    def grade_numeric(
        self,
        model_answer: str,
        correct_answer: str,
        criteria: Dict
    ) -> GradingResult:
        """
        Grade using numeric comparison.
        
        Criteria options:
        - tolerance (float): Absolute tolerance (default: 0.01)
        - relative_tolerance (float): Relative tolerance (default: 0.0)
        
        Args:
            model_answer: Model's response
            correct_answer: Expected answer
            criteria: Grading criteria
            
        Returns:
            GradingResult
        """
        tolerance = criteria.get("tolerance", 0.01)
        relative_tolerance = criteria.get("relative_tolerance", 0.0)
        
        try:
            # Extract numbers from answers
            model_num = self._extract_number(model_answer)
            correct_num = self._extract_number(correct_answer)
            
            if model_num is None:
                return GradingResult(
                    is_correct=False,
                    score=0.0,
                    explanation="Could not extract number from model answer",
                    details={"model_answer": model_answer}
                )
            
            if correct_num is None:
                return GradingResult(
                    is_correct=False,
                    score=0.0,
                    explanation="Could not extract number from correct answer",
                    details={"correct_answer": correct_answer}
                )
            
            # Calculate difference
            diff = abs(model_num - correct_num)
            
            # Check absolute tolerance
            within_absolute = diff <= tolerance
            
            # Check relative tolerance
            within_relative = True
            if relative_tolerance > 0 and correct_num != 0:
                relative_diff = diff / abs(correct_num)
                within_relative = relative_diff <= relative_tolerance
            
            is_correct = within_absolute and within_relative
            
            # Calculate partial credit based on how close the answer is
            if not is_correct and correct_num != 0:
                # Give partial credit for being close
                error_ratio = diff / abs(correct_num)
                if error_ratio < 0.5:  # Within 50% of correct
                    partial_credit = max(0.0, 1.0 - error_ratio)
                else:
                    partial_credit = 0.0
            else:
                partial_credit = 0.0
            
            return GradingResult(
                is_correct=is_correct,
                score=1.0 if is_correct else 0.0,
                partial_credit=partial_credit,
                explanation=f"Numeric comparison: {model_num} vs {correct_num} (diff={diff:.6f})",
                details={
                    "model_number": model_num,
                    "correct_number": correct_num,
                    "difference": diff,
                    "tolerance": tolerance,
                    "within_tolerance": is_correct
                }
            )
        
        except Exception as e:
            logger.error(f"Error in numeric grading: {e}")
            return GradingResult(
                is_correct=False,
                score=0.0,
                explanation=f"Numeric grading error: {e}",
                details={"error": str(e)}
            )
    
    def grade_semantic(
        self,
        model_answer: str,
        correct_answer: str,
        criteria: Dict
    ) -> GradingResult:
        """
        Grade using semantic similarity (basic implementation).
        
        Uses simple word overlap for now. Can be enhanced with
        embeddings/transformers in future phases.
        
        Criteria options:
        - threshold (float): Similarity threshold (default: 0.6)
        
        Args:
            model_answer: Model's response
            correct_answer: Expected answer
            criteria: Grading criteria
            
        Returns:
            GradingResult
        """
        threshold = criteria.get("threshold", 0.6)
        
        # Simple word-based similarity
        model_words = set(model_answer.lower().split())
        correct_words = set(correct_answer.lower().split())
        
        if not correct_words:
            return GradingResult(
                is_correct=False,
                score=0.0,
                explanation="Empty correct answer"
            )
        
        # Calculate Jaccard similarity
        intersection = model_words & correct_words
        union = model_words | correct_words
        
        if not union:
            similarity = 0.0
        else:
            similarity = len(intersection) / len(union)
        
        is_correct = similarity >= threshold
        
        return GradingResult(
            is_correct=is_correct,
            score=similarity,
            partial_credit=similarity if not is_correct else 0.0,
            explanation=f"Semantic similarity: {similarity:.2f} (threshold: {threshold})",
            details={
                "similarity": similarity,
                "threshold": threshold,
                "common_words": list(intersection),
                "model_words": len(model_words),
                "correct_words": len(correct_words)
            }
        )
    
    def grade_code(
        self,
        model_answer: str,
        correct_answer: str,
        criteria: Dict
    ) -> GradingResult:
        """
        Grade code answers (basic implementation).
        
        For now, uses normalized string comparison.
        Future phases can add code execution and testing.
        
        Args:
            model_answer: Model's code
            correct_answer: Expected code
            criteria: Grading criteria
            
        Returns:
            GradingResult
        """
        # Normalize code (remove extra whitespace, standardize indentation)
        model_normalized = self._normalize_code(model_answer)
        correct_normalized = self._normalize_code(correct_answer)
        
        is_correct = model_normalized == correct_normalized
        
        # Calculate partial credit based on string similarity
        if not is_correct:
            model_lines = set(model_normalized.split('\n'))
            correct_lines = set(correct_normalized.split('\n'))
            
            if correct_lines:
                line_overlap = len(model_lines & correct_lines) / len(correct_lines)
            else:
                line_overlap = 0.0
        else:
            line_overlap = 0.0
        
        return GradingResult(
            is_correct=is_correct,
            score=1.0 if is_correct else 0.0,
            partial_credit=line_overlap if not is_correct else 0.0,
            explanation="Code comparison (normalized)",
            details={
                "exact_match": is_correct,
                "line_overlap": line_overlap
            }
        )
    
    def _extract_number(self, text: str) -> Optional[float]:
        """Extract a number from text."""
        # Remove common non-numeric characters
        text = text.replace(',', '').replace('$', '').replace('%', '')
        
        # Try to find a number
        match = re.search(r'-?\d+\.?\d*', text)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison."""
        lines = []
        for line in code.split('\n'):
            # Strip trailing whitespace
            line = line.rstrip()
            # Skip empty lines
            if line.strip():
                lines.append(line)
        return '\n'.join(lines)
