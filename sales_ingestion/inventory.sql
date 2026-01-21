SELECT
    id,
    brand,
    garment_type,
    size_label,
    condition,
    estimated_resale_price
FROM clothing_items
ORDER BY created_at DESC;
