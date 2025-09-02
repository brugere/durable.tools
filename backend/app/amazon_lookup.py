"""
Amazon Product Lookup Service
Searches Amazon for washing machines and returns product data for affiliate linking
"""

import asyncio
import aiohttp
import re
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import quote_plus, urlparse, parse_qs
import time
import random

logger = logging.getLogger(__name__)

class AmazonProductLookup:
    """Service to find Amazon products for washing machines"""
    
    def __init__(self, affiliate_tag: str = "lebrugere-21"):
        self.affiliate_tag = affiliate_tag
        self.base_url = "https://www.amazon.fr"
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _build_search_url(self, brand: str, model: str) -> str:
        """Build Amazon search URL for brand + model"""
        search_query = f"{brand} {model}".strip()
        encoded_query = quote_plus(search_query)
        return f"{self.base_url}/s?k={encoded_query}&tag={self.affiliate_tag}"
    
    def _extract_asin_from_url(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon product URL"""
        # Pattern: /dp/XXXXXXXXXX or /gp/product/XXXXXXXXXX
        asin_patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})'
        ]
        
        for pattern in asin_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _extract_product_data(self, html: str) -> Optional[Dict[str, Any]]:
        """Extract product data from Amazon search results HTML"""
        try:
            # Look for the first product result
            # This is a simplified parser - in production you might want to use a more robust solution
            
            # Extract ASIN from data attributes
            asin_match = re.search(r'data-asin="([A-Z0-9]{10})"', html)
            if not asin_match:
                return None
                
            asin = asin_match.group(1)
            
            # Extract product title
            title_match = re.search(r'<span[^>]*class="[^"]*a-text-normal[^"]*"[^>]*>([^<]+)</span>', html)
            title = title_match.group(1).strip() if title_match else None
            
            # Extract image URL
            img_match = re.search(r'<img[^>]*src="([^"]*)"[^>]*data-image-latency="[^"]*"', html)
            img_url = img_match.group(1) if img_match else None
            
            # Extract price (simplified)
            price_match = re.search(r'<span[^>]*class="[^"]*a-price-whole[^"]*"[^>]*>([^<]+)</span>', html)
            price_text = price_match.group(1).replace('\xa0', '').replace(',', '.') if price_match else None
            price = float(price_text) if price_text and price_text.replace('.', '').isdigit() else None
            
            # Build direct product URL with affiliate tag
            product_url = f"{self.base_url}/dp/{asin}?tag={self.affiliate_tag}"
            
            return {
                "asin": asin,
                "title": title,
                "image_url": img_url,
                "price_eur": price,
                "product_url": product_url
            }
            
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            return None
    
    async def search_product(self, brand: str, model: str) -> Optional[Dict[str, Any]]:
        """Search Amazon for a specific washing machine and return product data"""
        try:
            search_url = self._build_search_url(brand, model)
            logger.info(f"Searching Amazon for: {brand} {model}")
            
            # Add random delay to be respectful
            await asyncio.sleep(random.uniform(1, 3))
            
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    logger.warning(f"Amazon search failed with status {response.status}")
                    return None
                    
                html = await response.text()
                
                # Check if we got a valid HTML response
                if "amazon" not in html.lower() or len(html) < 1000:
                    logger.warning("Invalid response from Amazon")
                    return None
                
                product_data = self._extract_product_data(html)
                if product_data:
                    logger.info(f"Found product: {product_data['asin']} - {product_data['title']}")
                    return product_data
                else:
                    logger.info(f"No product found for: {brand} {model}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error searching Amazon for {brand} {model}: {e}")
            return None
    
    async def batch_search_products(self, machines: List[Dict[str, Any]], 
                                   max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """Search multiple machines concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def search_with_semaphore(machine):
            async with semaphore:
                brand = machine.get('nom_metteur_sur_le_marche', '')
                model = machine.get('nom_modele', machine.get('id_unique', ''))
                
                if not brand or not model:
                    return machine
                
                product_data = await self.search_product(brand, model)
                if product_data:
                    machine.update({
                        'amazon_asin': product_data['asin'],
                        'amazon_product_url': product_data['product_url'],
                        'amazon_image_url': product_data['image_url'],
                        'amazon_price_eur': product_data['price_eur'],
                        'amazon_product_title': product_data['title'],
                        'amazon_last_checked': time.time()
                    })
                
                return machine
        
        tasks = [search_with_semaphore(machine) for machine in machines]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Search failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
