#!/usr/bin/env python3
"""
Amazon Data Enrichment Script
Enriches existing washing machine data with Amazon product information
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.duckdb_utils import get_connection
from app.amazon_lookup import AmazonProductLookup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def get_machines_without_amazon_data(limit: int = 100) -> list:
    """Get machines that don't have Amazon data yet"""
    try:
        conn = get_connection(readonly=True)
        
        # Get machines without Amazon data, prioritizing popular brands
        sql = """
            SELECT 
                id,
                nom_modele,
                nom_metteur_sur_le_marche,
                id_unique,
                amazon_asin,
                amazon_last_checked
            FROM washing_machines 
            WHERE (amazon_asin IS NULL OR amazon_asin = '')
            AND nom_metteur_sur_le_marche IS NOT NULL 
            AND nom_metteur_sur_le_marche != ''
            AND nom_modele IS NOT NULL 
            AND nom_modele != ''
            ORDER BY 
                CASE 
                    WHEN nom_metteur_sur_le_marche ILIKE '%samsung%' THEN 1
                    WHEN nom_metteur_sur_le_marche ILIKE '%lg%' THEN 2
                    WHEN nom_metteur_sur_le_marche ILIKE '%bosch%' THEN 3
                    WHEN nom_metteur_sur_le_marche ILIKE '%whirlpool%' THEN 4
                    WHEN nom_metteur_sur_le_marche ILIKE '%electrolux%' THEN 5
                    ELSE 6
                END,
                note_reparabilite DESC NULLS LAST
            LIMIT ?
        """
        
        result = conn.execute(sql, [limit]).fetchall()
        machines = []
        
        for row in result:
            machines.append({
                'id': row[0],
                'nom_modele': row[1],
                'nom_metteur_sur_le_marche': row[2],
                'id_unique': row[3],
                'amazon_asin': row[4],
                'amazon_last_checked': row[5]
            })
        
        logger.info(f"Found {len(machines)} machines without Amazon data")
        return machines
        
    except Exception as e:
        logger.error(f"Error getting machines: {e}")
        return []

async def update_machine_amazon_data(machine_id: int, amazon_data: dict):
    """Update a machine with Amazon product data"""
    try:
        conn = get_connection(readonly=False)
        
        sql = """
            UPDATE washing_machines 
            SET 
                amazon_asin = ?,
                amazon_product_url = ?,
                amazon_image_url = ?,
                amazon_price_eur = ?,
                amazon_product_title = ?,
                amazon_last_checked = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        conn.execute(sql, [
            amazon_data.get('asin'),
            amazon_data.get('product_url'),
            amazon_data.get('image_url'),
            amazon_data.get('price_eur'),
            amazon_data.get('title'),
            machine_id
        ])
        
        # Commit the transaction
        conn.commit()
        
        logger.info(f"Updated machine {machine_id} with Amazon data: {amazon_data.get('asin')}")
        
    except Exception as e:
        logger.error(f"Error updating machine {machine_id}: {e}")
    finally:
        conn.close()

async def enrich_amazon_data(batch_size: int = 10, max_machines: int = 100):
    """Main function to enrich washing machine data with Amazon information"""
    logger.info("Starting Amazon data enrichment...")
    
    # Get machines that need enrichment
    machines = await get_machines_without_amazon_data(max_machines)
    
    if not machines:
        logger.info("No machines found that need Amazon data enrichment")
        return
    
    # Process in batches
    for i in range(0, len(machines), batch_size):
        batch = machines[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(machines) + batch_size - 1)//batch_size}")
        
        async with AmazonProductLookup() as lookup:
            enriched_batch = await lookup.batch_search_products(batch, max_concurrent=3)
            
            # Update database with results
            for machine in enriched_batch:
                if machine.get('amazon_asin'):
                    # Create amazon_data dict from the machine data
                    amazon_data = {
                        'asin': machine.get('amazon_asin'),
                        'product_url': machine.get('amazon_product_url'),
                        'image_url': machine.get('amazon_image_url'),
                        'price_eur': machine.get('amazon_price_eur'),
                        'title': machine.get('amazon_product_title')
                    }
                    await update_machine_amazon_data(machine['id'], amazon_data)
            
            # Progress update
            processed = min(i + batch_size, len(machines))
            logger.info(f"Processed {processed}/{len(machines)} machines")
            
            # Small delay between batches
            if i + batch_size < len(machines):
                await asyncio.sleep(2)
    
    logger.info("Amazon data enrichment completed!")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrich washing machine data with Amazon product information')
    parser.add_argument('--batch-size', type=int, default=10, help='Number of machines to process per batch')
    parser.add_argument('--max-machines', type=int, default=100, help='Maximum number of machines to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without making changes')
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        machines = await get_machines_without_amazon_data(args.max_machines)
        logger.info(f"Would process {len(machines)} machines")
        for machine in machines[:5]:  # Show first 5
            logger.info(f"  - {machine['nom_metteur_sur_le_marche']} {machine['nom_modele']}")
        return
    
    await enrich_amazon_data(args.batch_size, args.max_machines)

if __name__ == "__main__":
    asyncio.run(main())
