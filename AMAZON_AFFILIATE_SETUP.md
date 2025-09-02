# Amazon Affiliate System Setup Guide

This guide explains how to set up and use the new Amazon affiliate system that provides direct product links instead of generic search links.

## 🎯 What This System Does

1. **Direct Product Links**: Instead of sending users to Amazon search results, users go directly to the specific washing machine product page
2. **Product Images**: Automatically fetches and displays Amazon product images on your website
3. **Pricing Information**: Shows current Amazon prices when available
4. **Higher Conversion**: Direct product links typically have much higher conversion rates than search links

## 🚀 Quick Start

### 1. Run the Database Migration

First, apply the database migration to add Amazon product fields:

```bash
cd backend
# If using DuckDB directly
duckdb washing_machines.duckdb < migrations/002_add_amazon_product_data.sql
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Test the Amazon Lookup

Test if the Amazon product lookup is working:

```bash
cd ..
python test_amazon_lookup.py
```

This will test searching for a few washing machines and show you what data is found.

### 4. Enrich Your Existing Data

Run the data enrichment script to populate Amazon data for existing washing machines:

```bash
cd backend/scripts
python enrich_amazon_data.py --batch-size 5 --max-machines 20
```

**Options:**
- `--batch-size`: Number of machines to process per batch (default: 10)
- `--max-machines`: Maximum total machines to process (default: 100)
- `--dry-run`: Show what would be processed without making changes

## 🔧 How It Works

### Database Schema

The system adds these new fields to your `washing_machines` table:

- `amazon_asin`: Amazon Standard Identification Number
- `amazon_product_url`: Direct Amazon product URL with your affiliate tag
- `amazon_image_url`: Product image URL from Amazon
- `amazon_price_eur`: Current price in EUR (if available)
- `amazon_product_title`: Amazon product title
- `amazon_last_checked`: When the data was last updated

### Affiliate Link Priority

The system automatically chooses the best available link:

1. **Direct Product URL** (if `amazon_product_url` exists)
2. **ASIN-based URL** (if `amazon_asin` exists)
3. **Search URL** (fallback to generic search)

### Frontend Display

- **Product Images**: Automatically displayed when available
- **Pricing**: Shows current Amazon price
- **Link Quality Indicator**: Shows "✓ Lien direct vers le produit" for direct links
- **Fallback Handling**: Gracefully handles missing Amazon data

## 📊 Data Enrichment Process

### What Gets Enriched

The system prioritizes machines by:
1. Popular brands (Samsung, LG, Bosch, etc.)
2. Higher repairability scores
3. Machines without existing Amazon data

### Rate Limiting

- **Concurrent requests**: Limited to 3 at a time
- **Delays**: 1-3 seconds between requests (respectful to Amazon)
- **Batch processing**: Processes machines in configurable batches

### Error Handling

- **Failed requests**: Logged but don't stop the process
- **Invalid responses**: Automatically detected and skipped
- **Retry logic**: Built-in resilience for temporary failures

## 🎨 Frontend Integration

### MachineResults Component

- Shows product images when available
- Displays Amazon prices
- Indicates direct vs. search links
- Fallback to placeholder images

### MachineDetails Component

- Dedicated product image section
- Prominent buy button with direct links
- Price and product title display
- Link quality indicators

## 🔍 Monitoring and Maintenance

### Check Enrichment Status

```sql
-- See how many machines have Amazon data
SELECT 
  COUNT(*) as total_machines,
  COUNT(amazon_asin) as with_amazon_data,
  COUNT(*) - COUNT(amazon_asin) as without_amazon_data
FROM washing_machines;

-- See recently updated machines
SELECT 
  nom_metteur_sur_le_marche,
  nom_modele,
  amazon_last_checked,
  amazon_asin
FROM washing_machines 
WHERE amazon_asin IS NOT NULL
ORDER BY amazon_last_checked DESC
LIMIT 10;
```

### Regular Updates

Run the enrichment script periodically to:
- Add Amazon data for new machines
- Update prices and availability
- Refresh product information

```bash
# Weekly update (example cron job)
0 2 * * 1 cd /path/to/durable.tools/backend/scripts && python enrich_amazon_data.py --max-machines 100
```

## ⚠️ Important Notes

### Amazon Terms of Service

- **Rate limiting**: Built-in delays to be respectful
- **User agents**: Rotates realistic browser user agents
- **Error handling**: Gracefully handles Amazon's anti-bot measures

### Data Quality

- **Image URLs**: May expire, system handles gracefully
- **Prices**: Can change frequently
- **Availability**: Products may become unavailable

### Fallback Strategy

- **No Amazon data**: Falls back to search links
- **Failed images**: Shows placeholder icons
- **Missing prices**: Price section hidden

## 🚀 Production Deployment

### Environment Variables

```bash
# Optional: Customize affiliate tag
AMAZON_AFFILIATE_TAG=lebrugere-21

# Optional: Customize marketplace
AMAZON_LOCALE=fr
```

### Performance Considerations

- **Database indexes**: Already created for optimal performance
- **Caching**: Consider Redis for frequently accessed Amazon data
- **CDN**: Product images can be cached via CDN

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're in the correct directory
2. **No results**: Check if Amazon is blocking requests
3. **Database errors**: Verify migration was applied correctly

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```bash
# Test just the Amazon lookup
python test_amazon_lookup.py

# Test database connection
cd backend && python -c "from app.database import get_connection; print('DB OK')"
```

## 📈 Expected Results

### Before (Generic Search Links)
- Users land on Amazon search results
- Lower conversion rates
- No product images
- No pricing information

### After (Direct Product Links)
- Users land directly on product pages
- **Higher conversion rates** (typically 2-5x improvement)
- **Product images** displayed on your site
- **Current pricing** shown to users
- **Better user experience** and trust

## 🎉 Success Metrics

Track these improvements:
- **Click-through rates** on buy buttons
- **Conversion rates** from your site to Amazon
- **User engagement** with product listings
- **Revenue per visitor** increase

---

**Need help?** Check the logs or run the test script to diagnose issues.
