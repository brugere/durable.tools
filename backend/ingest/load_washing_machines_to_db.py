#!/usr/bin/env python3
"""
Load washing machine data from raw CSV files into PostgreSQL database.

This script reads all CSV files from backend/data/raw/ and loads them into
the washing_machines table in PostgreSQL.
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
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

def get_csv_files(data_dir: str = "backend/data/raw") -> List[str]:
    """Get all CSV files from the data directory."""
    csv_files = []
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(data_dir, file))
    return sorted(csv_files)

def detect_separator(file_path: str) -> str:
    """Detect the separator used in the CSV file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        if ';' in first_line:
            return ';'
        elif ',' in first_line:
            return ','
        else:
            return ','  # default

def clean_column_name(col: str) -> str:
    """Clean column names to match database schema."""
    # Replace dots with underscores for PostgreSQL compatibility
    return col.replace('.', '_')

def load_csv_to_dataframe(file_path: str) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame with proper encoding and separator detection."""
    try:
        separator = detect_separator(file_path)
        logger.info(f"Loading {file_path} with separator '{separator}'")
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, sep=separator, encoding=encoding, low_memory=False)
                logger.info(f"Successfully loaded with encoding {encoding}")
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"Failed to load with encoding {encoding}: {e}")
                continue
        
        raise Exception(f"Could not load {file_path} with any encoding")
        
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        raise

def prepare_dataframe_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare DataFrame for database insertion."""
    # Clean column names
    df.columns = [clean_column_name(col) for col in df.columns]
    
    # Convert date columns
    if 'date_calcul' in df.columns:
        df['date_calcul'] = pd.to_datetime(df['date_calcul'], errors='coerce')
    
    # Convert numeric columns
    numeric_columns = ['note_id', 'note_reparabilite', 'note_fiabilite']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert integer columns (delai_jours and nb_annees columns)
    for col in df.columns:
        if 'delai_jours' in col or 'nb_annees' in col:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    
    # Convert float columns (note_* columns)
    for col in df.columns:
        if col.startswith('note_'):
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert boolean columns
    if 'is_orga' in df.columns:
        df['is_orga'] = df['is_orga'].map({'true': True, 'false': False, True: True, False: False})
    
    # Convert timestamp columns
    timestamp_columns = ['last_modified', 'created_at']
    for col in timestamp_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def insert_dataframe_to_db(df: pd.DataFrame, conn) -> int:
    """Insert DataFrame into the washing_machines table."""
    cursor = conn.cursor()
    
    # Get column names that exist in the database
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'washing_machines' 
        AND column_name != 'id'
        AND column_name != 'created_at_db'
        AND column_name != 'updated_at_db'
        ORDER BY ordinal_position
    """)
    db_columns = [row[0] for row in cursor.fetchall()]
    
    # Filter DataFrame to only include columns that exist in the database
    available_columns = [col for col in df.columns if col in db_columns]
    df_filtered = df[available_columns]
    
    # Create the INSERT statement
    columns_str = ', '.join(available_columns)
    placeholders = ', '.join(['%s'] * len(available_columns))
    
    insert_sql = f"""
        INSERT INTO washing_machines ({columns_str})
        VALUES ({placeholders})
    """
    
    # Convert DataFrame to list of tuples for insertion
    records = df_filtered.to_dict('records')
    values_list = []
    
    for record in records:
        values = []
        for col in available_columns:
            value = record.get(col)
            # Handle NaN values
            if pd.isna(value):
                values.append(None)
            else:
                values.append(value)
        values_list.append(tuple(values))
    
    # Insert data
    try:
        cursor.executemany(insert_sql, values_list)
        conn.commit()
        inserted_count = len(values_list)
        logger.info(f"Successfully inserted {inserted_count} records")
        return inserted_count
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to insert data: {e}")
        raise
    finally:
        cursor.close()

def main():
    """Main function to load all CSV files into the database."""
    logger.info("Starting washing machine data ingestion...")
    
    # Get CSV files
    csv_files = get_csv_files()
    if not csv_files:
        logger.error("No CSV files found in backend/data/raw/")
        return
    
    logger.info(f"Found {len(csv_files)} CSV files to process")
    
    # Connect to database
    conn = get_db_connection()
    
    total_inserted = 0
    
    try:
        for file_path in csv_files:
            logger.info(f"Processing {os.path.basename(file_path)}...")
            
            try:
                # Load CSV
                df = load_csv_to_dataframe(file_path)
                logger.info(f"Loaded {len(df)} rows from {os.path.basename(file_path)}")
                
                # Prepare data
                df = prepare_dataframe_for_db(df)
                
                # Insert into database
                inserted_count = insert_dataframe_to_db(df, conn)
                total_inserted += inserted_count
                
                logger.info(f"Successfully processed {os.path.basename(file_path)}")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                continue
    
    finally:
        conn.close()
    
    logger.info(f"Ingestion completed! Total records inserted: {total_inserted}")

if __name__ == "__main__":
    main() 