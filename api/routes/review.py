"""
Weekly Review API Route
=======================
GET /api/finance/review         - Current week review (JSON)
GET /api/finance/review?week=YYYY-MM-DD  - Specific week
"""

import sys
sys.path.insert(0, '/opt/mythos/finance')

from fastapi import APIRouter, Query
from weekly_review import generate_review, DecimalEncoder
import json

router = APIRouter()


@router.get("/review")
async def get_weekly_review(week: str = Query(None, description="Week start date YYYY-MM-DD")):
    """Generate weekly financial review."""
    review = generate_review(week)
    # FastAPI handles serialization but Decimal needs help
    return json.loads(json.dumps(review, cls=DecimalEncoder))
