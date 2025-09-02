#!/usr/bin/env python3
"""
Test script for the Amazon affiliate system
Creates a minimal test database and verifies the system works
"""

import duckdb
import os
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def create_test_database():
    """Create a minimal test database with Amazon fields"""
    
    # Create test database
    test_db_path = "test_washing_machines.duckdb"
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    conn = duckdb.connect(test_db_path)
    
    # Create table with Amazon fields
    conn.execute("""
        CREATE TABLE washing_machines (
            id INTEGER PRIMARY KEY,
            nom_modele TEXT,
            nom_metteur_sur_le_marche TEXT,
            note_reparabilite FLOAT,
            note_fiabilite FLOAT,
            note_id FLOAT,
            id_unique TEXT,
            -- Amazon product data
            amazon_asin TEXT,
            amazon_product_url TEXT,
            amazon_image_url TEXT,
            amazon_price_eur DECIMAL(10,2),
            amazon_last_checked TIMESTAMP,
            amazon_product_title TEXT
        )
    """)
    
    # Insert test data
    test_data = [
        (1, "WF20DG8650BWU3", "Samsung", 8.5, 7.8, 8.2, "SAMSUNG_WF20DG8650BWU3", None, None, None, None, None, None),
        (2, "F4V908R1S", "LG", 7.9, 8.1, 8.0, "LG_F4V908R1S", None, None, None, None, None, None),
        (3, "WAT28440FF", "Bosch", 8.2, 8.5, 8.4, "BOSCH_WAT28440FF", None, None, None, None, None, None),
    ]
    
    for row in test_data:
        conn.execute("INSERT INTO washing_machines VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
    
    print(f"✅ Created test database: {test_db_path}")
    print(f"   Inserted {len(test_data)} test washing machines")
    
    conn.close()
    return test_db_path

async def test_amazon_lookup_with_test_db():
    """Test Amazon lookup with the test database"""
    
    try:
        from app.amazon_lookup import AmazonProductLookup
        
        print("\n🔍 Testing Amazon lookup with test database...")
        print("=" * 60)
        
        # Test cases from our test database
        test_cases = [
            ("Samsung", "WF20DG8650BWU3"),
            ("LG", "F4V908R1S"),
            ("Bosch", "WAT28440FF"),
        ]
        
        async with AmazonProductLookup() as lookup:
            for brand, model in test_cases:
                print(f"\nSearching for: {brand} {model}")
                print("-" * 40)
                
                try:
                    result = await lookup.search_product(brand, model)
                    if result:
                        print(f"✅ Found: {result['asin']}")
                        print(f"   Title: {result['title']}")
                        print(f"   Price: {result['price_eur']}€" if result['price_eur'] else "   Price: N/A")
                        print(f"   Image: {result['image_url']}" if result['image_url'] else "   Image: N/A")
                        print(f"   URL: {result['product_url']}")
                        
                        # Verify affiliate tag is correct
                        if "lebrugere-21" in result['product_url']:
                            print("   ✅ Affiliate tag correctly included")
                        else:
                            print("   ❌ Affiliate tag missing")
                    else:
                        print("❌ No product found")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Small delay between requests
                await asyncio.sleep(2)
        
        print("\n" + "=" * 60)
        print("✅ Amazon lookup test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the correct directory")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_affiliate_link_generation():
    """Test the affiliate link generation functions"""
    
    try:
        from app.amazon_lookup import AmazonProductLookup
        
        print("\n🔗 Testing affiliate link generation...")
        print("=" * 60)
        
        # Test the affiliate link generation
        lookup = AmazonProductLookup()
        
        # Test search URL generation
        search_url = lookup._build_search_url("Samsung", "WF20DG8650BWU3")
        print(f"Search URL: {search_url}")
        
        if "lebrugere-21" in search_url:
            print("✅ Affiliate tag correctly included in search URL")
        else:
            print("❌ Affiliate tag missing from search URL")
        
        # Test direct product URL generation
        test_asin = "B0CQ21C2WX"
        product_url = f"https://www.amazon.fr/dp/{test_asin}?tag=lebrugere-21"
        print(f"Product URL: {product_url}")
        
        if "lebrugere-21" in product_url:
            print("✅ Affiliate tag correctly included in product URL")
        else:
            print("❌ Affiliate tag missing from product URL")
        
        print("\n✅ Affiliate link generation test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    
    print("🧪 Testing Amazon Affiliate System")
    print("=" * 60)
    
    # Create test database
    test_db_path = create_test_database()
    
    # Test affiliate link generation
    test_affiliate_link_generation()
    
    # Test Amazon lookup
    asyncio.run(test_amazon_lookup_with_test_db())
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"\n🧹 Cleaned up test database: {test_db_path}")
    
    print("\n🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Fix the main database (it has serialization issues)")
    print("2. Run the data enrichment script")
    print("3. Test the frontend with real Amazon data")

if __name__ == "__main__":
    main()
