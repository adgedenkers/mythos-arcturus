"""
Test Loader

Load and save test suites from JSON files and database.

Example:
    loader = TestLoader()
    
    # From JSON file
    suite = await loader.load_from_json("math_suite.json")
    
    # To database
    await loader.save_to_database(suite)
    
    # From database
    suite = await loader.load_from_database("suite_abc123")
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from database import db
from utils import generate_id, safe_json_dumps, safe_json_loads
from bench.test_question import TestQuestion
from bench.test_suite import TestSuite

logger = logging.getLogger(__name__)


class TestLoader:
    """
    Load and save test suites from various sources.
    
    Handles JSON files and database storage.
    """
    
    def __init__(self):
        """Initialize test loader."""
        self.suites_dir = Path(settings.TEST_SUITES_DIR)
        self.suites_dir.mkdir(parents=True, exist_ok=True)
    
    def load_from_json(self, filepath: str) -> TestSuite:
        """
        Load test suite from JSON file.
        
        Args:
            filepath: Path to JSON file (relative to TEST_SUITES_DIR or absolute)
            
        Returns:
            TestSuite instance
            
        Example:
            suite = loader.load_from_json("math/basic_arithmetic.json")
        """
        # Handle relative paths
        path = Path(filepath)
        if not path.is_absolute():
            path = self.suites_dir / filepath
        
        if not path.exists():
            raise FileNotFoundError(f"Test suite file not found: {path}")
        
        logger.info(f"Loading test suite from {path}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        suite = TestSuite.from_dict(data)
        
        # Validate after loading
        is_valid, error = suite.validate()
        if not is_valid:
            raise ValueError(f"Invalid test suite: {error}")
        
        logger.info(f"Loaded suite '{suite.name}' with {len(suite)} questions")
        return suite
    
    def save_to_json(
        self,
        suite: TestSuite,
        filepath: Optional[str] = None
    ) -> Path:
        """
        Save test suite to JSON file.
        
        Args:
            suite: TestSuite to save
            filepath: Path to save to (auto-generated if None)
            
        Returns:
            Path where file was saved
            
        Example:
            path = loader.save_to_json(suite, "math/new_suite.json")
        """
        # Validate before saving
        is_valid, error = suite.validate()
        if not is_valid:
            raise ValueError(f"Cannot save invalid suite: {error}")
        
        # Auto-generate filename if not provided
        if filepath is None:
            filename = f"{suite.category}_{suite.suite_id}.json"
            path = self.suites_dir / filename
        else:
            path = Path(filepath)
            if not path.is_absolute():
                path = self.suites_dir / filepath
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving test suite to {path}")
        
        # Convert to dict and save
        data = suite.to_dict(include_questions=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved suite '{suite.name}' with {len(suite)} questions")
        return path
    
    async def load_from_database(self, suite_id: str) -> TestSuite:
        """
        Load test suite from database.
        
        Args:
            suite_id: Suite identifier
            
        Returns:
            TestSuite instance
        """
        logger.info(f"Loading suite {suite_id} from database")
        
        # Get suite metadata
        suite_row = await db.fetchrow("""
            SELECT * FROM orch_test_suites WHERE suite_id = $1
        """, suite_id)
        
        if not suite_row:
            raise ValueError(f"Suite {suite_id} not found in database")
        
        # Create suite
        suite = TestSuite(
            name=suite_row["name"],
            category=suite_row["category"],
            description=suite_row["description"],
            suite_id=suite_row["suite_id"],
            version=suite_row["version"],
            public=suite_row["public"],
            created_by=suite_row["created_by"]
        )
        
        # Load questions
        question_rows = await db.fetch("""
            SELECT * FROM orch_test_questions
            WHERE suite_id = $1
            ORDER BY created_at
        """, suite_id)
        
        for row in question_rows:
            grading_criteria = safe_json_loads(row["grading_criteria"], {})
            metadata = safe_json_loads(row["metadata"], {})
            
            question = TestQuestion(
                text=row["question_text"],
                correct_answer=row["correct_answer"],
                answer_type=row["answer_type"],
                question_id=row["question_id"],
                difficulty=row["difficulty"],
                tags=row["tags"] or [],
                grading_criteria=grading_criteria,
                metadata=metadata
            )
            suite.add_question(question)
        
        logger.info(f"Loaded suite '{suite.name}' with {len(suite)} questions from database")
        return suite
    
    async def save_to_database(self, suite: TestSuite) -> str:
        """
        Save test suite to database.
        
        Args:
            suite: TestSuite to save
            
        Returns:
            suite_id
        """
        # Validate before saving
        is_valid, error = suite.validate()
        if not is_valid:
            raise ValueError(f"Cannot save invalid suite: {error}")
        
        logger.info(f"Saving suite '{suite.name}' to database")
        
        # Save suite metadata
        await db.execute("""
            INSERT INTO orch_test_suites (
                suite_id, name, category, description,
                question_count, difficulty, version,
                public, created_by, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (suite_id) DO UPDATE SET
                name = EXCLUDED.name,
                category = EXCLUDED.category,
                description = EXCLUDED.description,
                question_count = EXCLUDED.question_count,
                version = EXCLUDED.version,
                public = EXCLUDED.public
        """, suite.suite_id, suite.name, suite.category, suite.description,
             len(suite.questions), None, suite.version, suite.public,
             suite.created_by, suite.created_at)
        
        # Delete existing questions (we'll re-insert)
        await db.execute("""
            DELETE FROM orch_test_questions WHERE suite_id = $1
        """, suite.suite_id)
        
        # Save questions
        for question in suite.questions:
            grading_criteria_json = safe_json_dumps(question.grading_criteria)
            metadata_json = safe_json_dumps(question.metadata)
            
            await db.execute("""
                INSERT INTO orch_test_questions (
                    question_id, suite_id, question_text,
                    correct_answer, answer_type, grading_criteria,
                    difficulty, tags, metadata, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, question.question_id, suite.suite_id, question.text,
                 question.correct_answer, question.answer_type, grading_criteria_json,
                 question.difficulty, question.tags, metadata_json, question.created_at)
        
        logger.info(f"Saved suite '{suite.name}' with {len(suite)} questions to database")
        return suite.suite_id
    
    async def list_suites(
        self,
        category: Optional[str] = None,
        public_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List available test suites from database.
        
        Args:
            category: Filter by category
            public_only: Only return public suites
            
        Returns:
            List of suite metadata dicts
        """
        conditions = []
        params = []
        
        if category:
            conditions.append(f"category = ${len(params) + 1}")
            params.append(category)
        
        if public_only:
            conditions.append("public = true")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        rows = await db.fetch(f"""
            SELECT
                suite_id, name, category, description,
                question_count, version, public, created_by
            FROM orch_test_suites
            {where_clause}
            ORDER BY category, name
        """, *params)
        
        return [dict(row) for row in rows]
    
    def list_json_files(self, category: Optional[str] = None) -> List[Path]:
        """
        List available JSON test suite files.
        
        Args:
            category: Filter by category subdirectory
            
        Returns:
            List of file paths
        """
        if category:
            search_dir = self.suites_dir / category
        else:
            search_dir = self.suites_dir
        
        if not search_dir.exists():
            return []
        
        return sorted(search_dir.rglob("*.json"))
