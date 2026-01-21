SELECT
    COUNT(*) AS item_count,
    SUM(estimated_resale_price) AS total_estimated_resale_value
FROM clothing_items;
