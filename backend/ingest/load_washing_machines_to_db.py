#!/usr/bin/env python3
"""
Load washing machine data from raw CSV files into DuckDB database.

This script reads CSV files from a data directory and loads them into
 the washing_machines table in DuckDB.
"""

import os
import sys
import pandas as pd
import duckdb
from typing import List
import logging
from pathlib import Path

from app.duckdb_utils import get_connection

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ---------------- Path resolution ---------------- #

def _candidate_dirs() -> list[Path]:
    cwd = Path(os.getcwd())
    script_dir = Path(__file__).resolve().parent
    backend_dir = script_dir.parent

    candidates: list[Path] = []

    env_dir = os.environ.get("DATA_DIR")
    if env_dir:
        p = Path(env_dir)
        candidates.append(p if p.is_absolute() else cwd / p)

    candidates.append(cwd / "backend" / "data" / "raw")
    candidates.append(cwd / "data" / "raw")
    candidates.append(backend_dir / "data" / "raw")
    candidates.append(cwd / "data")

    out: list[Path] = []
    seen = set()
    for p in candidates:
        rp = p.resolve()
        if rp not in seen:
            out.append(rp)
            seen.add(rp)
    return out


def get_csv_files() -> List[str]:
    files: list[str] = []
    checked: list[str] = []
    for d in _candidate_dirs():
        checked.append(str(d))
        if d.exists() and d.is_dir():
            for file in sorted(d.glob("*.csv")):
                files.append(str(file))
    if not files:
        logger.error("No CSV files found. Checked: %s", ", ".join(checked))
    else:
        logger.info(
            "Found %d CSV files in: %s",
            len(files),
            ", ".join(sorted({str(Path(f).parent) for f in files})),
        )
    return files


# ---------------- CSV helpers ---------------- #

def detect_separator(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        first_line = f.readline().strip()
        if ';' in first_line:
            return ';'
        elif ',' in first_line:
            return ','
        else:
            return ','


def clean_column_name(col: str) -> str:
    return col.replace('.', '_')


def load_csv_to_dataframe(file_path: str) -> pd.DataFrame:
    separator = detect_separator(file_path)
    logger.info(f"Loading {file_path} with separator '{separator}'")
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, sep=separator, encoding=encoding, low_memory=False)
            logger.info(f"Successfully loaded with encoding {encoding}")
            return df
        except Exception as e:
            logger.warning(f"Failed to load with encoding {encoding}: {e}")
            continue
    raise Exception(f"Could not load {file_path} with any encoding")


# ---------------- Schema helpers ---------------- #

NUMERIC_COLUMNS_PREFIXES = ("note_")
NUMERIC_COLUMNS_EXACT = {"note_id", "note_reparabilite", "note_fiabilite"}
INTEGER_HINTS = ("delai_jours", "nb_annees")
DATE_COLUMNS = {"date_calcul"}


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [clean_column_name(col) for col in df.columns]

    for col in df.columns:
        if col in DATE_COLUMNS:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
        elif col in NUMERIC_COLUMNS_EXACT or col.startswith(NUMERIC_COLUMNS_PREFIXES) or any(h in col for h in INTEGER_HINTS):
            # Treat all numeric/integer-like as float to be permissive
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # else leave as object/string
    return df


def infer_duckdb_type(col: str, series: pd.Series) -> str:
    if col in DATE_COLUMNS:
        return "DATE"
    # All numeric and integer-like become DOUBLE to avoid cast errors
    if col in NUMERIC_COLUMNS_EXACT or col.startswith(NUMERIC_COLUMNS_PREFIXES) or any(h in col for h in INTEGER_HINTS):
        return "DOUBLE"
    return "VARCHAR"


def create_table_with_schema(conn, df: pd.DataFrame):
    cols_sql = ["id BIGINT"]
    for col in df.columns:
        dtype = infer_duckdb_type(col, df[col])
        cols_sql.append(f"{col} {dtype}")
    ddl = "CREATE TABLE washing_machines (" + ", ".join(cols_sql) + ")"
    conn.execute(ddl)


def ensure_id_column(conn):
    has_id = conn.execute(
        "SELECT COUNT(*) FROM pragma_table_info('washing_machines') WHERE name='id'"
    ).fetchone()[0]
    if not has_id:
        conn.execute("ALTER TABLE washing_machines ADD COLUMN id BIGINT")
        conn.execute(
            "UPDATE washing_machines SET id = row_number() OVER ()"
        )


def relax_integer_columns(conn):
    info = conn.execute("PRAGMA table_info('washing_machines')").fetchdf()
    integer_types = {"TINYINT", "SMALLINT", "INTEGER", "BIGINT"}
    for name, typ in zip(info['name'], info['type']):
        if name == 'id':
            continue
        if typ in integer_types:
            conn.execute(f"ALTER TABLE washing_machines ALTER COLUMN {name} TYPE DOUBLE")


def coerce_df_to_table_schema(conn, df: pd.DataFrame, current_id: int = 1) -> pd.DataFrame:
    info = conn.execute("PRAGMA table_info('washing_machines')").fetchdf()
    existing_cols = set(info['name'])

    # Add missing columns with permissive types
    for col in df.columns:
        if col not in existing_cols:
            duck_type = infer_duckdb_type(col, df[col])
            conn.execute(f"ALTER TABLE washing_machines ADD COLUMN {col} {duck_type}")
            existing_cols.add(col)

    # Refresh schema
    info = conn.execute("PRAGMA table_info('washing_machines')").fetchdf()
    type_map = dict(zip(info['name'], info['type']))

    # Build aligned DataFrame
    out_cols = {}
    for col, dtype in type_map.items():
        if col == 'id':
            # Generate sequential IDs starting from current_id
            out_cols[col] = pd.Series(range(current_id, current_id + len(df)))
        elif col not in df.columns:
            out_cols[col] = pd.Series([None] * len(df))
        else:
            s = df[col]
            if dtype in ("DOUBLE", "REAL", "DECIMAL"):
                s = pd.to_numeric(s, errors='coerce')
            elif dtype == "DATE":
                s = pd.to_datetime(s, errors='coerce').dt.date
            else:  # VARCHAR
                s = s.where(pd.notna(s), None).astype(object)
            out_cols[col] = s
    ordered_cols = list(type_map.keys())
    out = pd.DataFrame({c: out_cols.get(c, pd.Series([None] * len(df))) for c in ordered_cols})
    return out, ordered_cols


# ---------------- Write logic ---------------- #

def try_insert(conn, df: pd.DataFrame, current_id: int = 1) -> bool:
    df2, cols = coerce_df_to_table_schema(conn, df, current_id)
    conn.register("df", df2)
    placeholders = ", ".join(cols)
    try:
        conn.execute(f"INSERT INTO washing_machines ({placeholders}) SELECT {placeholders} FROM df")
        return True
    finally:
        conn.unregister("df")


def append_dataframe(conn, df: pd.DataFrame, current_id: int = 1):
    exists = conn.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='washing_machines'"
    ).fetchone()[0]
    if not exists:
        create_table_with_schema(conn, df)
    else:
        ensure_id_column(conn)

    # First attempt
    try:
        if try_insert(conn, df, current_id):
            return
    except Exception as e:
        err = str(e)
        logger.warning(f"First insert attempt failed, relaxing integer columns: {err}")

    # Relax integer columns and retry once
    relax_integer_columns(conn)
    if not try_insert(conn, df, current_id):
        conn.execute("SELECT 1")  # no-op for symmetry


# ---------------- Main ---------------- #

def main():
    logger.info("Starting washing machine data ingestion into DuckDB...")

    csv_files = get_csv_files()
    if not csv_files:
        return

    conn = get_connection()
    total = 0
    # Compute starting ID to avoid primary key collisions if table already exists
    try:
        table_exists = conn.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='washing_machines'"
        ).fetchone()[0]
        if table_exists:
            max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM washing_machines").fetchone()[0]
            current_id = int(max_id) + 1
        else:
            current_id = 1
    except Exception:
        current_id = 1
    
    for path in csv_files:
        try:
            df = load_csv_to_dataframe(path)
            df = prepare_dataframe(df)
            append_dataframe(conn, df, current_id)
            total += len(df)
            current_id += len(df)
            logger.info(f"Inserted {len(df)} rows from {os.path.basename(path)}")
        except Exception as e:
            logger.error(f"Failed to ingest {path}: {e}")
            continue

    logger.info(f"Ingestion completed. Total rows processed: {total}")


if __name__ == "__main__":
    main() 