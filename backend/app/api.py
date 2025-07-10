from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json

# Use absolute import for helpers from fetch_wmdi.py
from ingest.fetch_wmdi import load_dataset_as_dataframe, quick_insights, NpEncoder, fetch_all_datasets

router = APIRouter()

# Example static data matching frontend expectations
MACHINES = [
    {
        "id": 1,
        "brand": "Acme",
        "model_name": "Model X",
        "current_score": 8.5,
    },
    {
        "id": 2,
        "brand": "Beta",
        "model_name": "Model Y",
        "current_score": 7.2,
    },
]

@router.get("/machines", response_model=List[dict])
def get_machines(q: Optional[str] = None, limit: int = 25):
    # For now, ignore query params and return static data
    return MACHINES[:limit]

@router.get("/dataset/{dataset_id}")
def get_dataset_summary(dataset_id: str, limit: int = 100):
    """
    Fetch a dataset from data.gouv.fr by its ID and return a summary (quick_insights).
    Optionally limit the number of rows returned in the sample.
    """
    try:
        df = load_dataset_as_dataframe(dataset_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch dataset: {e}")
    summary = quick_insights(df)
    # Optionally limit the sample rows in the summary
    if "head" in summary and isinstance(summary["head"], list):
        summary["head"] = summary["head"][:limit]
    return json.loads(json.dumps(summary, cls=NpEncoder))

@router.get("/datasets")
def get_all_datasets(limit: int = 100):
    """
    Fetch a list of datasets from data.gouv.fr and return their metadata.
    """
    try:
        datasets = fetch_all_datasets(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch datasets: {e}")
    return json.loads(json.dumps(datasets, cls=NpEncoder)) 