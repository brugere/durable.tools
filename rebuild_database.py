#!/usr/bin/env python3
"""
Script to rebuild the washing machines database from data.gouv.fr
Downloads fresh data and creates a new database with Amazon product fields
"""

import os
import sys
import duckdb
import pandas as pd
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def download_washing_machine_data():
    """Download washing machine data from data.gouv.fr"""
    
    print("🌐 Downloading washing machine data from data.gouv.fr...")
    
    try:
        # Import the fetch functions
        from ingest.fetch_wmdi import download_all_washing_machine_data_raw
        
        # Download all datasets
        result = download_all_washing_machine_data_raw("data/raw")
        
        if result["downloaded"]:
            print(f"✅ Successfully downloaded {len(result['downloaded'])} datasets")
            return result["downloaded"]
        else:
            print("❌ No datasets were downloaded successfully")
            return []
            
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return []

def create_database_schema():
    """Create a simple database schema with basic washing machine fields"""
    
    # Create a simple schema with just the essential fields
    schema_sql = """
    CREATE TABLE IF NOT EXISTS washing_machines (
        id INTEGER PRIMARY KEY,
        nom_modele TEXT,
        nom_metteur_sur_le_marche TEXT,
        note_reparabilite FLOAT,
        note_fiabilite FLOAT,
        note_id FLOAT,
        id_unique TEXT,
        categorie_produit TEXT,
        date_calcul TEXT,
        url_tableau_detail_notation TEXT,
        
        -- Amazon affiliate fields
        amazon_asin TEXT,
        amazon_product_url TEXT,
        amazon_image_url TEXT,
        amazon_price_eur DECIMAL(10,2),
        amazon_last_checked TIMESTAMP,
        amazon_product_title TEXT,
        
        -- Additional fields for flexibility
        additional_data TEXT
    )
    """
    
    conn = duckdb.connect('backend/duckdb/washing_machines.duckdb')
    conn.execute(schema_sql)
    conn.close()
    print("✅ Database schema created successfully")

def load_data_to_database(downloaded_files):
    """Load the downloaded CSV files into the database"""
    
    if not downloaded_files:
        print("❌ No files to load")
        return
    
    print(f"\n📊 Loading {len(downloaded_files)} CSV files into database...")
    
    db_path = "backend/duckdb/washing_machines.duckdb"
    conn = duckdb.connect(db_path)
    
    total_rows = 0
    
    for file_info in downloaded_files:
        filepath = file_info["filepath"]
        print(f"\nProcessing: {os.path.basename(filepath)}")
        
        # Only process the consolidated file for now
        if "consolidés" not in filepath:
            print(f"  ⏭️  Skipping non-consolidated file")
            continue
            
        try:
            # Manual parsing of the consolidated CSV file
            with open(filepath, 'r', encoding='latin-1') as f:
                lines = f.readlines()
            
            if len(lines) < 2:
                print(f"  ⚠️  File too short, skipping")
                continue
            
            # Parse header (first line)
            header_line = lines[0].strip()
            column_names = [col.strip() for col in header_line.split(',')]
            print(f"  📋 Found {len(column_names)} columns")
            
            # Parse data lines
            data_rows = []
            for i, line in enumerate(lines[1:], 1):
                if line.strip():
                    # Simple comma split (this file doesn't have quoted fields with commas)
                    values = line.strip().split(',')
                    if len(values) >= len(column_names):
                        # Take only the columns we need
                        row_data = values[:len(column_names)]
                        data_rows.append(row_data)
                    else:
                        print(f"  ⚠️  Line {i} has {len(values)} values, expected {len(column_names)}")
            
            print(f"  📁 Loaded {len(data_rows)} rows from CSV")
            
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=column_names)
            
            # Clean column names (remove spaces, special chars)
            df.columns = [col.strip().replace(' ', '_').replace('(', '').replace(')', '') for col in df.columns]
            
            # Insert data into database
            for idx, row in df.iterrows():
                # Extract essential fields
                nom_modele = row.get('nom_modele', None)
                nom_metteur_sur_le_marche = row.get('nom_metteur_sur_le_marche', None)
                note_reparabilite = row.get('note_reparabilite', None)
                note_fiabilite = row.get('note_fiabilite', None)
                note_id = row.get('note_id', None)
                id_unique = row.get('id_unique', None)
                categorie_produit = row.get('categorie_produit', None)
                date_calcul = row.get('date_calcul', None)
                url_tableau_detail_notation = row.get('url_tableau_detail_notation', None)
                
                # Convert numeric fields
                try:
                    note_reparabilite = float(note_reparabilite) if note_reparabilite else None
                except:
                    note_reparabilite = None
                    
                try:
                    note_fiabilite = float(note_fiabilite) if note_fiabilite else None
                except:
                    note_fiabilite = None
                    
                try:
                    note_id = float(note_id) if note_id else None
                except:
                    note_id = None
                
                # Store all other data as JSON
                import json
                additional_data = {}
                for col in df.columns:
                    if col not in ['nom_modele', 'nom_metteur_sur_le_marche', 'note_reparabilite', 'note_fiabilite', 'note_id', 'id_unique', 'categorie_produit', 'date_calcul', 'url_tableau_detail_notation']:
                        value = row.get(col, None)
                        if value is not None and str(value).strip() != '':
                            additional_data[col] = value
                
                # Insert the row
                insert_data = {
                    'id': total_rows + 1,
                    'nom_modele': nom_modele,
                    'nom_metteur_sur_le_marche': nom_metteur_sur_le_marche,
                    'note_reparabilite': note_reparabilite,
                    'note_fiabilite': note_fiabilite,
                    'note_id': note_id,
                    'id_unique': id_unique,
                    'categorie_produit': categorie_produit,
                    'date_calcul': date_calcul,
                    'url_tableau_detail_notation': url_tableau_detail_notation,
                    'additional_data': json.dumps(additional_data) if additional_data else None
                }
                
                columns = list(insert_data.keys())
                values = list(insert_data.values())
                placeholders = ', '.join(['?' for _ in values])
                sql = f"INSERT INTO washing_machines ({', '.join(columns)}) VALUES ({placeholders})"
                conn.execute(sql, values)
                total_rows += 1
            
            print(f"  ✅ Inserted {len(df)} rows")
            
        except Exception as e:
            print(f"  ❌ Error processing file: {e}")
            import traceback
            traceback.print_exc()
    
    conn.close()
    print(f"\n✅ Total rows loaded: {total_rows}")

def main():
    """Main function to rebuild the database"""
    
    print("🏗️  Rebuilding Washing Machines Database")
    print("=" * 60)
    
    # Step 1: Download data
    downloaded_files = download_washing_machine_data()
    
    if not downloaded_files:
        print("❌ No data downloaded. Cannot proceed.")
        return
    
    # Step 2: Create database schema
    create_database_schema()
    
    # Step 3: Load data into database
    load_data_to_database(downloaded_files)
    
    print("\n🎉 Database rebuild completed successfully!")
    print("\nNext steps:")
    print("1. Test the database: python3 test_affiliate_system.py")
    print("2. Enrich with Amazon data: cd backend/scripts && python3 enrich_amazon_data.py")
    print("3. Start your local deployment to see the new affiliate links")

if __name__ == "__main__":
    main()
