from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json
import logging

logger = logging.getLogger(__name__)

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

# Mock data for fallback when database is not available
MOCK_MACHINES = [
    {
        "id": 1,
        "id_unique": "SAMSUNG-WF20DG8650BVU3",
        "nom_modele": "SAMSUNG WF20DG8650BVU3 Hublot",
        "nom_metteur_sur_le_marche": "SAMSUNG",
        "date_calcul": "2025-03-26",
        "note_reparabilite": 9.9,
        "note_fiabilite": 6.9,
        "note_id": 8.4,
        "categorie_produit": "Lave-linge",
        "url_tableau_detail_notation": "https://example.com/report1",
        "accessibilite_compteur_usage": "Accessible",
        "lien_documentation_professionnels": "https://example.com/pro-doc",
        "lien_documentation_particuliers": "https://example.com/user-doc",
        "note_A_c1": 9.5, "note_A_c2": 9.8, "note_A_c3": 9.2, "note_A_c4": 9.7,
        "note_B_c1": 6.5, "note_B_c2": 7.2, "note_B_c3": 7.0,
        "nom_piece_1_liste_2": "Moteur de lavage", "nom_piece_2_liste_2": "Pompe de vidange",
        "nom_piece_3_liste_2": "Électrovanne d'alimentation", "nom_piece_4_liste_2": "Capteur de niveau d'eau",
        "nom_piece_5_liste_2": "Carte électronique principale",
        "etape_demontage_piece_1_liste_2": "Débrancher l'alimentation, retirer le panneau arrière, déconnecter les câbles",
        "etape_demontage_piece_2_liste_2": "Vider l'eau, retirer le tuyau de vidange, dévisser la pompe",
        "etape_demontage_piece_3_liste_2": "Fermer l'alimentation d'eau, déconnecter les tuyaux, retirer l'électrovanne",
        "etape_demontage_piece_4_liste_2": "Retirer le panneau de commande, localiser le capteur, le déconnecter",
        "etape_demontage_piece_5_liste_2": "Débrancher tous les connecteurs, retirer les vis de fixation"
    },
    {
        "id": 2,
        "id_unique": "LG-FHT1408ZWL",
        "nom_modele": "LG FHT1408ZWL Hublot",
        "nom_metteur_sur_le_marche": "LG",
        "date_calcul": "2025-03-25",
        "note_reparabilite": 8.7,
        "note_fiabilite": 7.5,
        "note_id": 8.1,
        "categorie_produit": "Lave-linge",
        "url_tableau_detail_notation": "https://example.com/report2",
        "accessibilite_compteur_usage": "Accessible",
        "lien_documentation_professionnels": "https://example.com/lg-pro-doc",
        "lien_documentation_particuliers": "https://example.com/lg-user-doc",
        "note_A_c1": 8.5, "note_A_c2": 8.8, "note_A_c3": 8.2, "note_A_c4": 8.9,
        "note_B_c1": 7.0, "note_B_c2": 7.8, "note_B_c3": 7.5,
        "nom_piece_1_liste_2": "Moteur de lavage LG", "nom_piece_2_liste_2": "Pompe de vidange LG",
        "nom_piece_3_liste_2": "Électrovanne d'alimentation LG", "nom_piece_4_liste_2": "Capteur de niveau d'eau LG",
        "nom_piece_5_liste_2": "Carte électronique principale LG",
        "etape_demontage_piece_1_liste_2": "Retirer le panneau latéral, déconnecter les câbles du moteur",
        "etape_demontage_piece_2_liste_2": "Vider l'eau, retirer le tuyau, dévisser la pompe LG",
        "etape_demontage_piece_3_liste_2": "Fermer l'eau, déconnecter les tuyaux, retirer l'électrovanne LG",
        "etape_demontage_piece_4_liste_2": "Retirer le panneau, localiser le capteur LG",
        "etape_demontage_piece_5_liste_2": "Débrancher tous les connecteurs, retirer les vis LG"
    },
    {
        "id": 3,
        "id_unique": "BOSCH-WAT28400FF",
        "nom_modele": "BOSCH WAT28400FF Hublot",
        "nom_metteur_sur_le_marche": "BOSCH",
        "date_calcul": "2025-03-24",
        "note_reparabilite": 9.2,
        "note_fiabilite": 8.8,
        "note_id": 9.0,
        "categorie_produit": "Lave-linge",
        "url_tableau_detail_notation": "https://example.com/report3",
        "accessibilite_compteur_usage": "Accessible",
        "lien_documentation_professionnels": "https://example.com/bosch-pro-doc",
        "lien_documentation_particuliers": "https://example.com/bosch-user-doc",
        "note_A_c1": 9.0, "note_A_c2": 9.5, "note_A_c3": 8.8, "note_A_c4": 9.3,
        "note_B_c1": 8.5, "note_B_c2": 9.0, "note_B_c3": 8.9,
        "nom_piece_1_liste_2": "Moteur de lavage Bosch", "nom_piece_2_liste_2": "Pompe de vidange Bosch",
        "nom_piece_3_liste_2": "Électrovanne d'alimentation Bosch", "nom_piece_4_liste_2": "Capteur de niveau d'eau Bosch",
        "nom_piece_5_liste_2": "Carte électronique principale Bosch",
        "etape_demontage_piece_1_liste_2": "Retirer le panneau, déconnecter les câbles Bosch",
        "etape_demontage_piece_2_liste_2": "Vider l'eau, retirer le tuyau Bosch",
        "etape_demontage_piece_3_liste_2": "Fermer l'eau, déconnecter les tuyaux Bosch",
        "etape_demontage_piece_4_liste_2": "Retirer le panneau, localiser le capteur Bosch",
        "etape_demontage_piece_5_liste_2": "Débrancher tous les connecteurs Bosch"
    },
    {
        "id": 4,
        "id_unique": "WHIRLPOOL-FSCR12440",
        "nom_modele": "WHIRLPOOL FSCR12440 Top",
        "nom_metteur_sur_le_marche": "WHIRLPOOL",
        "date_calcul": "2025-03-23",
        "note_reparabilite": 7.8,
        "note_fiabilite": 8.2,
        "note_id": 8.0,
        "categorie_produit": "Lave-linge",
        "url_tableau_detail_notation": "https://example.com/report4",
        "accessibilite_compteur_usage": "Accessible",
        "lien_documentation_professionnels": "https://example.com/whirlpool-pro-doc",
        "lien_documentation_particuliers": "https://example.com/whirlpool-user-doc",
        "note_A_c1": 7.5, "note_A_c2": 8.0, "note_A_c3": 7.8, "note_A_c4": 8.2,
        "note_B_c1": 8.0, "note_B_c2": 8.5, "note_B_c3": 8.1,
        "nom_piece_1_liste_2": "Moteur de lavage Whirlpool", "nom_piece_2_liste_2": "Pompe de vidange Whirlpool",
        "nom_piece_3_liste_2": "Électrovanne d'alimentation Whirlpool", "nom_piece_4_liste_2": "Capteur de niveau d'eau Whirlpool",
        "nom_piece_5_liste_2": "Carte électronique principale Whirlpool",
        "etape_demontage_piece_1_liste_2": "Retirer le panneau, déconnecter les câbles Whirlpool",
        "etape_demontage_piece_2_liste_2": "Vider l'eau, retirer le tuyau Whirlpool",
        "etape_demontage_piece_3_liste_2": "Fermer l'eau, déconnecter les tuyaux Whirlpool",
        "etape_demontage_piece_4_liste_2": "Retirer le panneau, localiser le capteur Whirlpool",
        "etape_demontage_piece_5_liste_2": "Débrancher tous les connecteurs Whirlpool"
    },
    {
        "id": 5,
        "id_unique": "ELECTROLUX-EW6F1406I",
        "nom_modele": "ELECTROLUX EW6F1406I Hublot",
        "nom_metteur_sur_le_marche": "ELECTROLUX",
        "date_calcul": "2025-03-22",
        "note_reparabilite": 8.5,
        "note_fiabilite": 7.8,
        "note_id": 8.2,
        "categorie_produit": "Lave-linge",
        "url_tableau_detail_notation": "https://example.com/report5",
        "accessibilite_compteur_usage": "Accessible",
        "lien_documentation_professionnels": "https://example.com/electrolux-pro-doc",
        "lien_documentation_particuliers": "https://example.com/electrolux-user-doc",
        "note_A_c1": 8.2, "note_A_c2": 8.7, "note_A_c3": 8.0, "note_A_c4": 8.8,
        "note_B_c1": 7.5, "note_B_c2": 8.0, "note_B_c3": 7.9,
        "nom_piece_1_liste_2": "Moteur de lavage Electrolux", "nom_piece_2_liste_2": "Pompe de vidange Electrolux",
        "nom_piece_3_liste_2": "Électrovanne d'alimentation Electrolux", "nom_piece_4_liste_2": "Capteur de niveau d'eau Electrolux",
        "nom_piece_5_liste_2": "Carte électronique principale Electrolux",
        "etape_demontage_piece_1_liste_2": "Retirer le panneau, déconnecter les câbles Electrolux",
        "etape_demontage_piece_2_liste_2": "Vider l'eau, retirer le tuyau Electrolux",
        "etape_demontage_piece_3_liste_2": "Fermer l'eau, déconnecter les tuyaux Electrolux",
        "etape_demontage_piece_4_liste_2": "Retirer le panneau, localiser le capteur Electrolux",
        "etape_demontage_piece_5_liste_2": "Débrancher tous les connecteurs Electrolux"
    },
    {
        "id": 6,
        "id_unique": "CANDY-CS1412D3",
        "nom_modele": "CANDY CS1412D3 Hublot",
        "nom_metteur_sur_le_marche": "CANDY",
        "date_calcul": "2025-03-21",
        "note_reparabilite": 6.5,
        "note_fiabilite": 6.8,
        "note_id": 6.7,
        "categorie_produit": "Lave-linge",
        "url_tableau_detail_notation": "https://example.com/report6",
        "accessibilite_compteur_usage": "Accessible",
        "lien_documentation_professionnels": "https://example.com/candy-pro-doc",
        "lien_documentation_particuliers": "https://example.com/candy-user-doc",
        "note_A_c1": 6.0, "note_A_c2": 6.8, "note_A_c3": 6.2, "note_A_c4": 6.9,
        "note_B_c1": 6.5, "note_B_c2": 7.0, "note_B_c3": 6.9,
        "nom_piece_1_liste_2": "Moteur de lavage Candy", "nom_piece_2_liste_2": "Pompe de vidange Candy",
        "nom_piece_3_liste_2": "Électrovanne d'alimentation Candy", "nom_piece_4_liste_2": "Capteur de niveau d'eau Candy",
        "nom_piece_5_liste_2": "Carte électronique principale Candy",
        "etape_demontage_piece_1_liste_2": "Retirer le panneau, déconnecter les câbles Candy",
        "etape_demontage_piece_2_liste_2": "Vider l'eau, retirer le tuyau Candy",
        "etape_demontage_piece_3_liste_2": "Fermer l'eau, déconnecter les tuyaux Candy",
        "etape_demontage_piece_4_liste_2": "Retirer le panneau, localiser le capteur Candy",
        "etape_demontage_piece_5_liste_2": "Débrancher tous les connecteurs Candy"
    }
]

def get_mock_search_results(q=None, brand=None, model=None, min_repairability=None, max_repairability=None,
                          min_reliability=None, max_reliability=None, year=None, limit=50, offset=0, 
                          sort_by="note_reparabilite", sort_order="DESC"):
    """Fallback function that provides mock search results when database is unavailable."""
    filtered_machines = MOCK_MACHINES.copy()
    
    # Apply filters
    if q:
        query_lower = q.lower()
        # Check if it's a special filter query
        if any(keyword in query_lower for keyword in ["réparable", "repairability"]):
            # Filter by repairability
            filtered_machines = [m for m in filtered_machines if m["note_reparabilite"] >= 7.0]
            # Sort by repairability
            filtered_machines.sort(key=lambda x: x["note_reparabilite"], reverse=True)
        elif any(keyword in query_lower for keyword in ["fiable", "reliability"]):
            # Filter by reliability
            filtered_machines = [m for m in filtered_machines if m["note_fiabilite"] >= 6.0]
            # Sort by reliability
            filtered_machines.sort(key=lambda x: x["note_fiabilite"], reverse=True)
        elif any(keyword in query_lower for keyword in ["durable", "durability"]):
            # Filter by overall durability (global score)
            filtered_machines = [m for m in filtered_machines if m["note_id"] >= 7.0]
            # Sort by global score
            filtered_machines.sort(key=lambda x: x["note_id"], reverse=True)
        elif any(keyword in query_lower for keyword in ["excellent", "meilleur"]):
            # Filter for excellent machines (high scores across all categories)
            filtered_machines = [m for m in filtered_machines if m["note_reparabilite"] >= 8.0 and m["note_fiabilite"] >= 7.0]
            # Sort by global score
            filtered_machines.sort(key=lambda x: x["note_id"], reverse=True)
        elif any(keyword in query_lower for keyword in ["bon marché", "économique"]):
            # Filter for affordable machines (lower scores but still decent)
            filtered_machines = [m for m in filtered_machines if m["note_reparabilite"] <= 6.0 and m["note_fiabilite"] <= 6.0]
            # Sort by global score
            filtered_machines.sort(key=lambda x: x["note_id"], reverse=True)
        elif any(keyword in query_lower for keyword in ["hublot", "top", "front", "charge"]):
            # Filter by loading type
            filtered_machines = [m for m in filtered_machines if keyword in m["nom_modele"].lower()]
        else:
            # General text search
            filtered_machines = [m for m in filtered_machines if 
                               query_lower in m["nom_modele"].lower() or 
                               query_lower in m["nom_metteur_sur_le_marche"].lower()]
    
    if brand:
        filtered_machines = [m for m in filtered_machines if brand.lower() in m["nom_metteur_sur_le_marche"].lower()]
    
    if min_repairability is not None:
        filtered_machines = [m for m in filtered_machines if m["note_reparabilite"] >= min_repairability]
    
    if max_repairability is not None:
        filtered_machines = [m for m in filtered_machines if m["note_reparabilite"] <= max_repairability]
    
    if min_reliability is not None:
        filtered_machines = [m for m in filtered_machines if m["note_fiabilite"] >= min_reliability]
    
    if max_reliability is not None:
        filtered_machines = [m for m in filtered_machines if m["note_fiabilite"] <= max_reliability]
    
    # Apply sorting
    if sort_by == "note_reparabilite":
        filtered_machines.sort(key=lambda x: x["note_reparabilite"], reverse=(sort_order == "DESC"))
    elif sort_by == "note_fiabilite":
        filtered_machines.sort(key=lambda x: x["note_fiabilite"], reverse=(sort_order == "DESC"))
    elif sort_by == "note_id":
        filtered_machines.sort(key=lambda x: x["note_id"], reverse=(sort_order == "DESC"))
    elif sort_by == "date_calcul":
        filtered_machines.sort(key=lambda x: x["date_calcul"], reverse=(sort_order == "DESC"))
    else:
        # Default sort by repairability
        filtered_machines.sort(key=lambda x: x["note_reparabilite"], reverse=True)
    
    # Apply limit and offset
    start_idx = offset
    end_idx = start_idx + limit
    limited_machines = filtered_machines[start_idx:end_idx]
    
    return {
        "machines": limited_machines,
        "total": len(filtered_machines),
        "limit": limit,
        "offset": offset,
        "has_more": end_idx < len(filtered_machines)
    }

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
        # Use real database search with enhanced logic
        try:
            # Enhanced search logic for database
            enhanced_min_repairability = min_repairability
            enhanced_max_repairability = max_repairability
            enhanced_min_reliability = min_reliability
            enhanced_max_reliability = max_reliability
            enhanced_sort_by = sort_by
            enhanced_sort_order = sort_order
            
            if q:
                query_lower = q.lower()
                # Check if it's a special filter query
                if any(keyword in query_lower for keyword in ["réparable", "repairability", "plus réparable", "plus reparable"]):
                    # Filter by repairability
                    enhanced_min_repairability = 7.0
                    enhanced_sort_by = "note_reparabilite"
                    enhanced_sort_order = "DESC"
                    # Clear the query parameter to avoid text search
                    q = None
                elif any(keyword in query_lower for keyword in ["fiable", "reliability", "plus fiable", "plus reliable"]):
                    # Filter by reliability
                    enhanced_min_reliability = 6.0
                    enhanced_sort_by = "note_fiabilite"
                    enhanced_sort_order = "DESC"
                    # Clear the query parameter to avoid text search
                    q = None
                elif any(keyword in query_lower for keyword in ["durable", "durability"]):
                    # Filter by overall durability (global score)
                    enhanced_sort_by = "note_id"
                    enhanced_sort_order = "DESC"
                    # Clear the query parameter to avoid text search
                    q = None
                elif any(keyword in query_lower for keyword in ["excellent", "meilleur"]):
                    # Filter for excellent machines (high scores across all categories)
                    enhanced_min_repairability = 8.0
                    enhanced_min_reliability = 7.0
                    enhanced_sort_by = "note_id"
                    enhanced_sort_order = "DESC"
                    # Clear the query parameter to avoid text search
                    q = None
                elif any(keyword in query_lower for keyword in ["bon marché", "économique"]):
                    # Filter for affordable machines (lower scores but still decent)
                    enhanced_max_repairability = 6.0
                    enhanced_max_reliability = 6.0
                    enhanced_sort_by = "note_id"
                    enhanced_sort_order = "DESC"
                    # Clear the query parameter to avoid text search
                    q = None
                elif any(keyword in query_lower for keyword in ["hublot", "top", "front", "charge"]):
                    # Filter by loading type - use general search
                    pass
                else:
                    # General text search - use existing q parameter
                    pass
            
            return search_washing_machines(
                query=q,
                brand=brand,
                model=model,
                min_repairability=enhanced_min_repairability,
                max_repairability=enhanced_max_repairability,
                min_reliability=enhanced_min_reliability,
                max_reliability=enhanced_max_reliability,
                year=year,
                limit=limit,
                offset=offset,
                sort_by=enhanced_sort_by,
                sort_order=enhanced_sort_order
            )
        except Exception as e:
            # Fallback to mock data if database fails
            logger.error(f"Database search failed, falling back to mock data: {e}")
            return get_mock_search_results(q, brand, model, min_repairability, max_repairability, 
                                        min_reliability, max_reliability, year, limit, offset, sort_by, sort_order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/machines/{machine_id}")
def get_machine(machine_id: int):
    """
    Get detailed information about a specific washing machine.
    """
    try:
        # Try to get machine from database
        machine = get_machine_details(machine_id)
        if machine is None:
            raise HTTPException(status_code=404, detail="Machine not found")
        return machine
    except HTTPException:
        raise
    except Exception as e:
        # Fallback to mock data if database fails
        logger.error(f"Database query failed, falling back to mock data: {e}")
        machine = next((m for m in MOCK_MACHINES if m["id"] == machine_id), None)
        if machine is None:
            raise HTTPException(status_code=404, detail="Machine not found")
        return machine

@router.get("/brands")
def get_all_brands():
    """
    Get list of all unique brands/manufacturers.
    """
    try:
        # Try to get brands from database
        return {"brands": get_brands()}
    except Exception as e:
        # Fallback to mock data if database fails
        logger.error(f"Database query failed, falling back to mock data: {e}")
        brands = list(set(m["nom_metteur_sur_le_marche"] for m in MOCK_MACHINES))
        return {"brands": brands}

@router.get("/statistics")
def get_db_statistics():
    """
    Get statistics about the washing machines database.
    """
    try:
        # Try to get statistics from database
        return get_statistics()
    except Exception as e:
        # Fallback to mock data if database fails
        logger.error(f"Database query failed, falling back to mock data: {e}")
        repairability_scores = [m["note_reparabilite"] for m in MOCK_MACHINES]
        reliability_scores = [m["note_fiabilite"] for m in MOCK_MACHINES]
        
        stats = {
            "total_machines": len(MOCK_MACHINES),
            "total_brands": len(set(m["nom_metteur_sur_le_marche"] for m in MOCK_MACHINES)),
            "avg_repairability": sum(repairability_scores) / len(repairability_scores),
            "avg_reliability": sum(reliability_scores) / len(reliability_scores),
            "min_repairability": min(repairability_scores),
            "max_repairability": max(repairability_scores),
            "min_reliability": min(reliability_scores),
            "max_reliability": max(reliability_scores)
        }
        
        return {
            "statistics": stats,
            "top_brands_by_repairability": [
                {
                    "nom_metteur_sur_le_marche": m["nom_metteur_sur_le_marche"],
                    "avg_repairability": m["note_reparabilite"],
                    "machine_count": 1
                }
                for m in MOCK_MACHINES
            ]
        } 