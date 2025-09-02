#!/usr/bin/env python3
"""
Script to apply the Amazon product data migration
"""

import duckdb
import os
from pathlib import Path

def apply_migration():
    """Apply the Amazon product data migration"""
    
    # Database path
    db_path = "backend/duckdb/washing_machines.duckdb"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("Please make sure the database exists and the path is correct.")
        return False
    
    # Migration SQL
    migration_sql = """
    -- Add Amazon product data fields
    ALTER TABLE washing_machines ADD COLUMN IF NOT EXISTS amazon_asin TEXT;
    ALTER TABLE washing_machines ADD COLUMN IF NOT EXISTS amazon_product_url TEXT;
    ALTER TABLE washing_machines ADD COLUMN IF NOT EXISTS amazon_image_url TEXT;
    ALTER TABLE washing_machines ADD COLUMN IF NOT EXISTS amazon_price_eur DECIMAL(10,2);
    ALTER TABLE washing_machines ADD COLUMN IF NOT EXISTS amazon_last_checked TIMESTAMP;
    ALTER TABLE washing_machines ADD COLUMN IF NOT EXISTS amazon_product_title TEXT;
    
    -- Create indexes for better performance (ignore if they exist)
    CREATE INDEX IF NOT EXISTS idx_washing_machines_amazon_asin ON washing_machines(amazon_asin);
    CREATE INDEX IF NOT EXISTS idx_washing_machines_amazon_last_checked ON washing_machines(amazon_last_checked);
    
    -- Add local image path column
    ALTER TABLE washing_machines ADD COLUMN IF NOT EXISTS local_image_path TEXT;
    """
    
    try:
        print("🔧 Applying Amazon product data migration...")
        print(f"📁 Database: {db_path}")
        
        # Connect to database
        conn = duckdb.connect(db_path)
        
        # Check current table structure
        print("\n📊 Current table structure:")
        result = conn.execute("PRAGMA table_info(washing_machines)").fetchall()
        columns = [row[1] for row in result]
        print(f"   Found {len(columns)} columns")
        
        # Check if Amazon columns already exist
        amazon_columns = ['amazon_asin', 'amazon_product_url', 'amazon_image_url', 
                         'amazon_price_eur', 'amazon_last_checked', 'amazon_product_title']
        
        existing_amazon_columns = [col for col in amazon_columns if col in columns]
        if existing_amazon_columns:
            print(f"   ⚠️  Some Amazon columns already exist: {existing_amazon_columns}")
        
        # Apply migration
        print("\n🚀 Applying migration...")
        conn.execute(migration_sql)
        
        # Verify the changes
        print("\n✅ Migration completed! New table structure:")
        result = conn.execute("PRAGMA table_info(washing_machines)").fetchall()
        new_columns = [row[1] for row in result]
        
        # Show new Amazon columns
        new_amazon_columns = [col for col in amazon_columns if col in new_columns]
        print(f"   Amazon columns: {new_amazon_columns}")
        
        # Check total columns
        print(f"   Total columns: {len(new_columns)}")
        
        # Close connection
        conn.close()
        
        print("\n🎉 Migration successful!")
        print("\nNext steps:")
        print("1. Install backend dependencies: cd backend && pip install -r requirements.txt")
        print("2. Test Amazon lookup: python test_amazon_lookup.py")
        print("3. Enrich data: cd backend/scripts && python enrich_amazon_data.py --dry-run")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nTroubleshooting:")
        print("- Make sure the database file exists and is writable")
        print("- Check if you have write permissions to the database")
        print("- Verify the database is not locked by another process")
        return False

if __name__ == "__main__":
    success = apply_migration()
    exit(0 if success else 1)
