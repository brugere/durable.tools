import os
import duckdb
from typing import Optional


def get_duckdb_path() -> str:
    db_path = os.environ.get("DUCKDB_PATH", "/code/duckdb/washing_machines.duckdb")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path


def get_connection(readonly: bool = False) -> duckdb.DuckDBPyConnection:
    """Return a DuckDB connection to the on-disk database file."""
    db_path = get_duckdb_path()
    conn = duckdb.connect(db_path, read_only=readonly)
    conn.execute("PRAGMA threads=4")
    conn.execute("PRAGMA memory_limit='1GB'")
    return conn
