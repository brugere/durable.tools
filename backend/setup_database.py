#!/usr/bin/env python3
"""
Setup database: Run migration and load washing machine data.
"""

import os
import sys
import psycopg2
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'postgres'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def run_migration():
    """Run the database migration."""
    logger.info("Running database migration...")
    
    # Read the migration SQL
    migration_file = "migrations/001_create_washing_machines_table.sql"
    
    if not os.path.exists(migration_file):
        logger.error(f"Migration file not found: {migration_file}")
        return False
    
    try:
        # Read the migration SQL
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Connect to database and execute migration
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'washing_machines'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            logger.info("Table washing_machines already exists, skipping migration")
        else:
            # Execute the migration
            cursor.execute(migration_sql)
            logger.info("Migration completed successfully")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to run migration: {e}")
        return False

def load_data():
    """Load washing machine data into the database."""
    logger.info("Loading washing machine data...")
    
    try:
        # Import and run the ingestion script
        from ingest.load_washing_machines_to_db import main as load_main
        load_main()
        return True
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return False

def main():
    """Main function to set up the database."""
    logger.info("Starting database setup...")
    
    # Step 1: Run migration
    if not run_migration():
        logger.error("Migration failed. Exiting.")
        sys.exit(1)
    
    # Step 2: Load data
    if not load_data():
        logger.error("Data loading failed. Exiting.")
        sys.exit(1)
    
    logger.info("Database setup completed successfully!")

if __name__ == "__main__":
    main() 