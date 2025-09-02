-- Migration: Add Amazon product data fields
-- This adds fields to store Amazon product information for direct affiliate links

ALTER TABLE washing_machines ADD COLUMN amazon_asin TEXT;
ALTER TABLE washing_machines ADD COLUMN amazon_product_url TEXT;
ALTER TABLE washing_machines ADD COLUMN amazon_image_url TEXT;
ALTER TABLE washing_machines ADD COLUMN amazon_price_eur DECIMAL(10,2);
ALTER TABLE washing_machines ADD COLUMN amazon_last_checked TIMESTAMP;
ALTER TABLE washing_machines ADD COLUMN amazon_product_title TEXT;

-- Create indexes for better performance
CREATE INDEX idx_washing_machines_amazon_asin ON washing_machines(amazon_asin);
CREATE INDEX idx_washing_machines_amazon_last_checked ON washing_machines(amazon_last_checked);

-- Add a comment to document the new fields
COMMENT ON COLUMN washing_machines.amazon_asin IS 'Amazon Standard Identification Number for direct product linking';
COMMENT ON COLUMN washing_machines.amazon_product_url IS 'Direct Amazon product URL with affiliate tag';
COMMENT ON COLUMN washing_machines.amazon_image_url IS 'Amazon product image URL for website display';
COMMENT ON COLUMN washing_machines.amazon_price_eur IS 'Current Amazon price in EUR (if available)';
COMMENT ON COLUMN washing_machines.amazon_last_checked IS 'Timestamp when Amazon data was last updated';
COMMENT ON COLUMN washing_machines.amazon_product_title IS 'Amazon product title for display purposes';
