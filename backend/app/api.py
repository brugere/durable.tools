from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json

# Use absolute import for helpers from fetch_wmdi.py
from ingest.fetch_wmdi import (
    load_washing_machine_data, 
    quick_insights, 
    NpEncoder, 
    fetch_washing_machine_datasets,
    get_washing_machine_datasets_summary
)

# Import search functionality
from .search import (
    search_washing_machines,
    get_machine_details,
    get_brands,
    get_statistics
)

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

# Removed old static machines endpoint - replaced with database search

@router.get("/dataset/{dataset_id}")
def get_dataset_summary(dataset_id: str, limit: int = 100):
    """
    Fetch a washing machine durability dataset from data.gouv.fr by its ID and return a summary.
    """
    try:
        df = load_washing_machine_data(dataset_id)
        
        # Return a simplified summary
        return {
            "success": True,
            "shape": list(df.shape),
            "columns": [str(col) for col in df.columns],
            "sample_data": df.head(limit).to_dict(orient="records"),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": list(df.select_dtypes(include=['number']).columns),
            "categorical_columns": list(df.select_dtypes(include=['object']).columns)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch dataset: {str(e)}")


@router.get("/washing-machines")
def get_washing_machine_datasets():
    """
    Get a comprehensive summary of all washing machine durability datasets with their resources.
    """
    try:
        summary = get_washing_machine_datasets_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch washing machine datasets: {e}")
    return json.loads(json.dumps(summary, cls=NpEncoder))


@router.get("/test-dataset/{dataset_id}")
def test_dataset_loading(dataset_id: str):
    """
    Test endpoint to debug dataset loading issues.
    """
    try:
        df = load_washing_machine_data(dataset_id)
        return {
            "success": True,
            "shape": df.shape,
            "columns": list(df.columns[:5]),  # First 5 columns only
            "message": "Dataset loaded successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to load dataset"
        }

@router.get("/datasets")
def get_all_datasets(limit: int = 100):
    """
    Fetch a list of washing machine durability datasets from data.gouv.fr and return their metadata.
    """
    try:
        summary = get_washing_machine_datasets_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch datasets: {e}")
    return json.loads(json.dumps(summary, cls=NpEncoder))

# New search endpoints for washing machines database

@router.get("/machines")
def search_machines(
    q: Optional[str] = Query(None, description="General search query"),
    brand: Optional[str] = Query(None, description="Filter by brand/manufacturer"),
    model: Optional[str] = Query(None, description="Filter by model name"),
    min_repairability: Optional[float] = Query(None, description="Minimum repairability score"),
    max_repairability: Optional[float] = Query(None, description="Maximum repairability score"),
    min_reliability: Optional[float] = Query(None, description="Minimum reliability score"),
    max_reliability: Optional[float] = Query(None, description="Maximum reliability score"),
    year: Optional[int] = Query(None, description="Filter by year"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip"),
    sort_by: str = Query("note_reparabilite", description="Field to sort by"),
    sort_order: str = Query("DESC", description="Sort order (ASC or DESC)")
):
    """
    Search washing machines in the local database.
    
    Example queries:
    - /v1/machines?q=samsung&year=2025
    - /v1/machines?min_repairability=8.0&sort_by=note_reparabilite&sort_order=DESC
    - /v1/machines?brand=LG&limit=10
    """
    try:
        return search_washing_machines(
            query=q,
            brand=brand,
            model=model,
            min_repairability=min_repairability,
            max_repairability=max_repairability,
            min_reliability=min_reliability,
            max_reliability=max_reliability,
            year=year,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/machines/{machine_id}")
def get_machine(machine_id: int):
    """
    Get detailed information about a specific washing machine.
    """
    try:
        machine = get_machine_details(machine_id)
        if machine is None:
            raise HTTPException(status_code=404, detail="Machine not found")
        return machine
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get machine details: {str(e)}")

@router.get("/brands")
def get_all_brands():
    """
    Get list of all unique brands/manufacturers.
    """
    try:
        return {"brands": get_brands()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get brands: {str(e)}")

@router.get("/statistics")
def get_db_statistics():
    """
    Get statistics about the washing machines database.
    """
    try:
        return get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}") 