-- SQL ingestion file

BEGIN;

-- =========================================================
-- ITEM 1: Old Navy Flare / Micro-Flare (Dark Wash)
-- =========================================================

INSERT INTO clothing_items (
    id,
    brand,
    garment_type,
    gender_category,
    size_label,
    standardized_size,
    condition,
    country_of_manufacture,
    original_retail_price,
    estimated_resale_price,
    care_instructions,
    confidence_score,
    inferred_fields,
    notes
) VALUES (
    'a41e3f6e-3c7e-4c5b-b4c6-6a8b5c9e1001',
    'Old Navy',
    'jeans',
    'womens',
    '18 Regular',
    '18',
    'gently_used',
    NULL,
    NULL,
    18.00,
    NULL,
    0.90,
    ARRAY['season', 'estimated_resale_price'],
    'Old Navy flare / micro-flare, dark wash.'
);

INSERT INTO clothing_colors (item_id, color) VALUES
('a41e3f6e-3c7e-4c5b-b4c6-6a8b5c9e1001', 'dark blue');

INSERT INTO clothing_materials (item_id, material) VALUES
('a41e3f6e-3c7e-4c5b-b4c6-6a8b5c9e1001', 'cotton'),
('a41e3f6e-3c7e-4c5b-b4c6-6a8b5c9e1001', 'polyester'),
('a41e3f6e-3c7e-4c5b-b4c6-6a8b5c9e1001', 'elastane');

INSERT INTO clothing_images (item_id, filename, original_filename, view_type) VALUES
('a41e3f6e-3c7e-4c5b-b4c6-6a8b5c9e1001', 'image-0000010.jpeg', 'C8681257-B498-4EF3-BFA7-64DE4BBC912C.jpeg', 'front'),
('a41e3f6e-3c7e-4c5b-b4c6-6a8b5c9e1001', 'image-0000011.jpeg', '7238909D-5CF4-4E34-A68C-3B2F947C1663.jpeg', 'label'),
('a41e3f6e-3c7e-4c5b-b4c6-6a8b5c9e1001', 'image-0000012.jpeg', 'FB47054B-484B-47AE-8D71-0D96BCB638F8.jpeg', 'tag');

-- =========================================================
-- ITEM 2: Old Navy Micro-Flare (Light Wash)
-- =========================================================

INSERT INTO clothing_items (
    id,
    brand,
    garment_type,
    gender_category,
    size_label,
    standardized_size,
    condition,
    country_of_manufacture,
    original_retail_price,
    estimated_resale_price,
    care_instructions,
    confidence_score,
    inferred_fields,
    notes
) VALUES (
    'b52d7a91-9d3c-4c1f-9f6e-0d0f7c2a1002',
    'Old Navy',
    'jeans',
    'womens',
    '18 Regular',
    '18',
    'gently_used',
    NULL,
    NULL,
    17.00,
    NULL,
    0.88,
    ARRAY['season', 'estimated_resale_price'],
    'Old Navy micro-flare, lighter wash.'
);

INSERT INTO clothing_colors (item_id, color) VALUES
('b52d7a91-9d3c-4c1f-9f6e-0d0f7c2a1002', 'light blue');

INSERT INTO clothing_materials (item_id, material) VALUES
('b52d7a91-9d3c-4c1f-9f6e-0d0f7c2a1002', 'cotton'),
('b52d7a91-9d3c-4c1f-9f6e-0d0f7c2a1002', 'polyester'),
('b52d7a91-9d3c-4c1f-9f6e-0d0f7c2a1002', 'elastane');

INSERT INTO clothing_images (item_id, filename, original_filename, view_type) VALUES
('b52d7a91-9d3c-4c1f-9f6e-0d0f7c2a1002', 'image-0000013.jpeg', 'ECC5EDD7-DC40-43BE-BC83-39B78B67E254.jpeg', 'front'),
('b52d7a91-9d3c-4c1f-9f6e-0d0f7c2a1002', 'image-0000014.jpeg', '751DF0B6-880C-4F2D-92EA-5D32F4ABEC4A.jpeg', 'label'),
('b52d7a91-9d3c-4c1f-9f6e-0d0f7c2a1002', 'image-0000015.jpeg', 'E90468FB-8675-4058-A07F-7F6AF3C816F1.jpeg', 'tag');

-- =========================================================
-- ITEM 3: Gap 1969 Perfect Boot
-- =========================================================

INSERT INTO clothing_items (
    id,
    brand,
    garment_type,
    gender_category,
    size_label,
    standardized_size,
    condition,
    country_of_manufacture,
    original_retail_price,
    estimated_resale_price,
    care_instructions,
    confidence_score,
    inferred_fields,
    notes
) VALUES (
    'c9a84c33-7e9a-4c44-9c88-44a8c3101003',
    'Gap 1969',
    'jeans',
    'womens',
    '34R',
    '34R',
    'gently_used',
    NULL,
    NULL,
    28.00,
    NULL,
    0.91,
    ARRAY['materials', 'season', 'estimated_resale_price'],
    'Gap 1969 Perfect Boot cut.'
);

INSERT INTO clothing_colors (item_id, color) VALUES
('c9a84c33-7e9a-4c44-9c88-44a8c3101003', 'medium blue');

INSERT INTO clothing_materials (item_id, material) VALUES
('c9a84c33-7e9a-4c44-9c88-44a8c3101003', 'cotton blend');

INSERT INTO clothing_images (item_id, filename, original_filename, view_type) VALUES
('c9a84c33-7e9a-4c44-9c88-44a8c3101003', 'image-0000016.jpeg', '544EFEED-BBA6-4393-81B9-560207C7A909.jpeg', 'front'),
('c9a84c33-7e9a-4c44-9c88-44a8c3101003', 'image-0000017.jpeg', '5E0658E4-85A1-4209-BDF6-FA6DFDB04770.jpeg', 'label'),
('c9a84c33-7e9a-4c44-9c88-44a8c3101003', 'image-0000018.jpeg', '90E04AF9-18C3-4FCB-8A0C-2EDF2751F922.jpeg', 'tag');

COMMIT;
