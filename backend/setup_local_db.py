#!/usr/bin/env python3
"""
Setup local database with washing machine data from raw CSV files.
This script will create the DuckDB database and load all the washing machine data.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Setting up local DuckDB database with washing machine data...")
    
    # Set the working directory to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Set environment variable for DuckDB path
    os.environ['DUCKDB_PATH'] = str(backend_dir / 'duckdb' / 'washing_machines.duckdb')
    
    try:
        # Import the data loading function
        from ingest.load_washing_machines_to_db import main as load_main
        
        # Load the data
        logger.info("Loading washing machine data from CSV files...")
        load_main()
        
        logger.info("✅ Local database setup completed successfully!")
        logger.info(f"The database file is now available at: {os.environ['DUCKDB_PATH']}")
        
    except Exception as e:
        logger.error(f"❌ Failed to setup local database: {e}")
        logger.error("Make sure you have the required dependencies installed:")
        logger.error("pip install -r requirements.txt")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
