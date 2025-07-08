from fastapi import APIRouter
from typing import List, Optional

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