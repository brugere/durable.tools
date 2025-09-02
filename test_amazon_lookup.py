#!/usr/bin/env python3
"""
Test script for Amazon product lookup
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

async def test_amazon_lookup():
    """Test the Amazon product lookup service"""
    try:
        from app.amazon_lookup import AmazonProductLookup
        
        print("Testing Amazon product lookup...")
        print("=" * 50)
        
        # Test cases
        test_cases = [
            ("Samsung", "WF20DG8650BWU3"),
            ("LG", "F4V908R1S"),
            ("Bosch", "WAT28440FF"),
        ]
        
        async with AmazonProductLookup() as lookup:
            for brand, model in test_cases:
                print(f"\nSearching for: {brand} {model}")
                print("-" * 30)
                
                try:
                    result = await lookup.search_product(brand, model)
                    if result:
                        print(f"✅ Found: {result['asin']}")
                        print(f"   Title: {result['title']}")
                        print(f"   Price: {result['price_eur']}€" if result['price_eur'] else "   Price: N/A")
                        print(f"   Image: {result['image_url']}" if result['image_url'] else "   Image: N/A")
                        print(f"   URL: {result['product_url']}")
                    else:
                        print("❌ No product found")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Small delay between requests
                await asyncio.sleep(2)
        
        print("\n" + "=" * 50)
        print("Test completed!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the correct directory")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_amazon_lookup())
