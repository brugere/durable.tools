-- Migration: Add local image path for downloaded product images

ALTER TABLE washing_machines ADD COLUMN IF NOT EXISTS local_image_path TEXT;

COMMENT ON COLUMN washing_machines.local_image_path IS 'Relative path under frontend/public for the downloaded product image (e.g. /machines/123.jpg)';


