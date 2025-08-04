"""
Search functionality for washing machines database.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),  # Changed from 'localhost' to 'db'
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def search_washing_machines(
    query: Optional[str] = None,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    min_repairability: Optional[float] = None,
    max_repairability: Optional[float] = None,
    min_reliability: Optional[float] = None,
    max_reliability: Optional[float] = None,
    year: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "note_reparabilite",
    sort_order: str = "DESC"
) -> Dict[str, Any]:
    """
    Search washing machines in the database with various filters.
    
    Args:
        query: General search query (searches in model name and brand)
        brand: Filter by brand/manufacturer
        model: Filter by model name
        min_repairability: Minimum repairability score
        max_repairability: Maximum repairability score
        min_reliability: Minimum reliability score
        max_reliability: Maximum reliability score
        year: Filter by year (extracted from date_calcul)
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Field to sort by
        sort_order: Sort order (ASC or DESC)
    
    Returns:
        Dict with results and metadata
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build the WHERE clause
        conditions = []
        params = []
        param_count = 0
        
        if query:
            param_count += 1
            conditions.append(f"(nom_modele ILIKE %s OR nom_metteur_sur_le_marche ILIKE %s)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        if brand:
            param_count += 1
            conditions.append(f"nom_metteur_sur_le_marche ILIKE %s")
            params.append(f"%{brand}%")
        
        if model:
            param_count += 1
            conditions.append(f"nom_modele ILIKE %s")
            params.append(f"%{model}%")
        
        if min_repairability is not None:
            param_count += 1
            conditions.append(f"note_reparabilite >= %s")
            params.append(min_repairability)
        
        if max_repairability is not None:
            param_count += 1
            conditions.append(f"note_reparabilite <= %s")
            params.append(max_repairability)
        
        if min_reliability is not None:
            param_count += 1
            conditions.append(f"note_fiabilite >= %s")
            params.append(min_reliability)
        
        if max_reliability is not None:
            param_count += 1
            conditions.append(f"note_fiabilite <= %s")
            params.append(max_reliability)
        
        if year:
            param_count += 1
            conditions.append(f"EXTRACT(YEAR FROM date_calcul) = %s")
            params.append(year)
        
        # Build the SQL query
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Validate sort_by to prevent SQL injection
        allowed_sort_fields = {
            'nom_modele', 'nom_metteur_sur_le_marche', 'note_reparabilite', 
            'note_fiabilite', 'date_calcul', 'note_id'
        }
        if sort_by not in allowed_sort_fields:
            sort_by = 'note_reparabilite'
        
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        # Count total results
        count_sql = f"""
            SELECT COUNT(*) 
            FROM washing_machines 
            WHERE {where_clause}
        """
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()['count']
        
        # Get results
        sql = f"""
            SELECT 
                id,
                id_unique,
                nom_modele,
                nom_metteur_sur_le_marche,
                date_calcul,
                note_reparabilite,
                note_fiabilite,
                note_id,
                categorie_produit,
                url_tableau_detail_notation,
                accessibilite_compteur_usage,
                lien_documentation_professionnels,
                lien_documentation_particuliers
            FROM washing_machines 
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(sql, params + [limit, offset])
        results = cursor.fetchall()
        
        # Convert results to list of dicts
        machines = []
        for row in results:
            machine = dict(row)
            # Convert date to string for JSON serialization
            if machine['date_calcul']:
                machine['date_calcul'] = machine['date_calcul'].isoformat()
            machines.append(machine)
        
        cursor.close()
        conn.close()
        
        return {
            "machines": machines,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }
        
    except Exception as e:
        logger.error(f"Error searching washing machines: {e}")
        raise

def get_machine_details(machine_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific washing machine.
    
    Args:
        machine_id: The ID of the machine to retrieve
    
    Returns:
        Dict with machine details or None if not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        sql = """
            SELECT * FROM washing_machines WHERE id = %s
        """
        
        cursor.execute(sql, [machine_id])
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            machine = dict(result)
            # Convert date to string for JSON serialization
            if machine['date_calcul']:
                machine['date_calcul'] = machine['date_calcul'].isoformat()
            return machine
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting machine details: {e}")
        raise

def get_brands() -> List[str]:
    """
    Get list of all unique brands/manufacturers.
    
    Returns:
        List of brand names
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
            SELECT DISTINCT nom_metteur_sur_le_marche 
            FROM washing_machines 
            WHERE nom_metteur_sur_le_marche IS NOT NULL 
            AND nom_metteur_sur_le_marche != ''
            ORDER BY nom_metteur_sur_le_marche
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [row[0] for row in results]
        
    except Exception as e:
        logger.error(f"Error getting brands: {e}")
        raise

def get_statistics() -> Dict[str, Any]:
    """
    Get statistics about the washing machines database.
    
    Returns:
        Dict with various statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get basic stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_machines,
                COUNT(DISTINCT nom_metteur_sur_le_marche) as total_brands,
                AVG(note_reparabilite) as avg_repairability,
                AVG(note_fiabilite) as avg_reliability,
                MIN(note_reparabilite) as min_repairability,
                MAX(note_reparabilite) as max_repairability,
                MIN(note_fiabilite) as min_reliability,
                MAX(note_fiabilite) as max_reliability
            FROM washing_machines
            WHERE note_reparabilite IS NOT NULL AND note_fiabilite IS NOT NULL
        """)
        
        stats = dict(cursor.fetchone())
        
        # Get top brands by repairability
        cursor.execute("""
            SELECT 
                nom_metteur_sur_le_marche,
                AVG(note_reparabilite) as avg_repairability,
                COUNT(*) as machine_count
            FROM washing_machines
            WHERE note_reparabilite IS NOT NULL
            GROUP BY nom_metteur_sur_le_marche
            HAVING COUNT(*) >= 2
            ORDER BY avg_repairability DESC
            LIMIT 10
        """)
        
        top_brands = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            "statistics": stats,
            "top_brands_by_repairability": top_brands
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise 