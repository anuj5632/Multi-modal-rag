import os
import json
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/evaluate",
    tags=["evaluation"],
)

RESULTS_DIR = "eval_results"
LATEST_RESULTS_FILE = os.path.join(RESULTS_DIR, "latest.json")

os.makedirs(RESULTS_DIR, exist_ok=True)


class EvalTestCase(BaseModel):
    question: str
    ground_truth: Optional[str] = None


class EvalRequest(BaseModel):
    test_cases: List[EvalTestCase]
    top_k: int = 5


@router.post("")
def run_evaluation(request: EvalRequest):
    # Imported lazily so the app can start up (and the rest of the API
    # stay usable) even if ragas / langchain-google-genai aren't
    # installed yet - evaluation is opt-in tooling, not core to serving
    # chat requests.
    try:
        from app.evaluation.ragas_eval import run_evaluation as ragas_run
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Evaluation dependencies not installed: {e}. "
                   f"pip install ragas langchain-google-genai",
        )

    if not request.test_cases:
        raise HTTPException(status_code=400, detail="test_cases cannot be empty")

    test_cases = [tc.model_dump() for tc in request.test_cases]

    result = ragas_run(test_cases, top_k=request.top_k)

    result["run_at"] = datetime.now(timezone.utc).isoformat()

    with open(LATEST_RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)

    return result


@router.get("/results")
def get_latest_results():
    """Returns the results of the most recent /evaluate run, for a dashboard to poll/render."""
    if not os.path.exists(LATEST_RESULTS_FILE):
        raise HTTPException(status_code=404, detail="No evaluation has been run yet")

    with open(LATEST_RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
