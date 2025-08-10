"""
Search functionality for washing machines database using DuckDB.
"""

from typing import List, Dict, Any, Optional
import logging
import re
import duckdb

from .duckdb_utils import get_connection

logger = logging.getLogger(__name__)


def _sanitize_like(value: str) -> str:
    # DuckDB uses ILIKE for case-insensitive matches, but Python parameterization will handle quoting
    return f"%{value}%"


def _build_where_and_params(
    query: Optional[str],
    brand: Optional[str],
    model: Optional[str],
    min_repairability: Optional[float],
    max_repairability: Optional[float],
    min_reliability: Optional[float],
    max_reliability: Optional[float],
    year: Optional[int],
) -> tuple[str, list]:
    conditions = []
    params: list[Any] = []

    if query:
        conditions.append("(nom_modele ILIKE ? OR nom_metteur_sur_le_marche ILIKE ?)")
        like = _sanitize_like(query)
        params.extend([like, like])

    if brand:
        conditions.append("nom_metteur_sur_le_marche ILIKE ?")
        params.append(_sanitize_like(brand))

    if model:
        conditions.append("nom_modele ILIKE ?")
        params.append(_sanitize_like(model))

    if min_repairability is not None:
        conditions.append("note_reparabilite >= ?")
        params.append(min_repairability)

    if max_repairability is not None:
        conditions.append("note_reparabilite <= ?")
        params.append(max_repairability)

    if min_reliability is not None:
        conditions.append("note_fiabilite >= ?")
        params.append(min_reliability)

    if max_reliability is not None:
        conditions.append("note_fiabilite <= ?")
        params.append(max_reliability)

    if year is not None:
        # Cast date to year; DuckDB supports EXTRACT(YEAR FROM col)
        conditions.append("EXTRACT(YEAR FROM date_calcul) = ?")
        params.append(year)

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    return where_clause, params


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
    sort_order: str = "DESC",
) -> Dict[str, Any]:
    """Search washing machines in DuckDB.

    Returns a dict with keys: machines, total, limit, offset, has_more
    """
    try:
        conn = get_connection(readonly=True)

        allowed_sort_fields = {
            "nom_modele",
            "nom_metteur_sur_le_marche",
            "note_reparabilite",
            "note_fiabilite",
            "date_calcul",
            "note_id",
        }
        if sort_by not in allowed_sort_fields:
            sort_by = "note_reparabilite"
        sort_order = "DESC" if str(sort_order).upper() == "DESC" else "ASC"

        where_clause, params = _build_where_and_params(
            query, brand, model, min_repairability, max_repairability,
            min_reliability, max_reliability, year
        )

        count_sql = f"SELECT COUNT(*) AS cnt FROM washing_machines WHERE {where_clause}"
        total_count = conn.execute(count_sql, params).fetchone()[0]

        select_sql = f"""
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
                lien_documentation_particuliers,
                note_A_c1, note_A_c2, note_A_c3, note_A_c4,
                note_B_c1, note_B_c2, note_B_c3,
                nom_piece_1_liste_2, nom_piece_2_liste_2, nom_piece_3_liste_2,
                nom_piece_4_liste_2, nom_piece_5_liste_2
            FROM washing_machines
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(select_sql, params + [limit, offset]).fetchall()
        cols = [d[0] for d in conn.description]
        machines = [dict(zip(cols, r)) for r in rows]

        # Ensure ISO date strings
        for m in machines:
            if m.get("date_calcul") is not None:
                # DuckDB returns datetime/date as Python date/datetime; isoformat is fine
                m["date_calcul"] = m["date_calcul"].isoformat()

        return {
            "machines": machines,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count,
        }
    except Exception as e:
        logger.error(f"Error searching washing machines (duckdb): {e}")
        raise


def get_machine_details(machine_id: int) -> Optional[Dict[str, Any]]:
    try:
        conn = get_connection(readonly=True)
        sql = """
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
                lien_documentation_particuliers,
                note_A_c1, note_A_c2, note_A_c3, note_A_c4,
                note_B_c1, note_B_c2, note_B_c3,
                nom_piece_1_liste_2, nom_piece_2_liste_2, nom_piece_3_liste_2,
                nom_piece_4_liste_2, nom_piece_5_liste_2,
                etape_demontage_piece_1_liste_2, etape_demontage_piece_2_liste_2,
                etape_demontage_piece_3_liste_2, etape_demontage_piece_4_liste_2,
                etape_demontage_piece_5_liste_2
            FROM washing_machines WHERE id = ?
        """
        res = conn.execute(sql, [machine_id]).fetchone()
        if not res:
            return None
        cols = [d[0] for d in conn.description]
        m = dict(zip(cols, res))
        if m.get("date_calcul") is not None:
            m["date_calcul"] = m["date_calcul"].isoformat()
        return m
    except Exception as e:
        logger.error(f"Error getting machine details (duckdb): {e}")
        raise


def get_brands() -> List[str]:
    try:
        conn = get_connection(readonly=True)
        sql = (
            "SELECT DISTINCT nom_metteur_sur_le_marche "
            "FROM washing_machines "
            "WHERE nom_metteur_sur_le_marche IS NOT NULL "
            "AND nom_metteur_sur_le_marche != '' "
            "ORDER BY nom_metteur_sur_le_marche"
        )
        rows = conn.execute(sql).fetchall()
        return [r[0] for r in rows]
    except Exception as e:
        logger.error(f"Error getting brands (duckdb): {e}")
        raise


def get_statistics() -> Dict[str, Any]:
    try:
        conn = get_connection(readonly=True)
        stats_row = conn.execute(
            """
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
            """
        ).fetchone()

        cols = [d[0] for d in conn.description]
        stats = dict(zip(cols, stats_row))

        top_rows = conn.execute(
            """
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
            """
        ).fetchall()
        top_cols = [d[0] for d in conn.description]
        top_brands = [dict(zip(top_cols, r)) for r in top_rows]

        return {
            "statistics": stats,
            "top_brands_by_repairability": top_brands,
        }
    except Exception as e:
        logger.error(f"Error getting statistics (duckdb): {e}")
        raise 