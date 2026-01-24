#!/bin/bash
# ============================================================================
# MYTHOS DATABASE DIAGNOSTIC SCRIPT
# Captures complete state of clothing/shoes sales system
# ============================================================================

OUTPUT_FILE="/home/adge/mythos_diagnostic_$(date +%Y%m%d_%H%M%S).txt"

echo "============================================================================" > "$OUTPUT_FILE"
echo "MYTHOS DATABASE DIAGNOSTIC REPORT" >> "$OUTPUT_FILE"
echo "Generated: $(date)" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

# ============================================================================
# SECTION 1: TABLE STRUCTURES
# ============================================================================

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "SECTION 1: TABLE STRUCTURES" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "--- clothing_items table structure ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "\d clothing_items" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- clothing_colors table structure ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "\d clothing_colors" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- clothing_materials table structure ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "\d clothing_materials" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- clothing_images table structure ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "\d clothing_images" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- shoes_forsale table structure ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "\d shoes_forsale" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- shoe_colors table structure ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "\d shoe_colors" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- shoe_materials table structure ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "\d shoe_materials" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- shoe_images table structure ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "\d shoe_images" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- sales table structure ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "\d sales" >> "$OUTPUT_FILE" 2>&1

# ============================================================================
# SECTION 2: ALL TABLE DATA
# ============================================================================

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "SECTION 2: ALL TABLE DATA" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "--- ALL clothing_items ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM clothing_items;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- ALL clothing_colors ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM clothing_colors;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- ALL clothing_materials ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM clothing_materials;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- ALL clothing_images ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM clothing_images;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- ALL shoes_forsale ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM shoes_forsale;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- ALL shoe_colors ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM shoe_colors;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- ALL shoe_materials ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM shoe_materials;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- ALL shoe_images ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM shoe_images;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- ALL sales ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM sales;" >> "$OUTPUT_FILE" 2>&1

# ============================================================================
# SECTION 3: VIEWS
# ============================================================================

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "SECTION 3: VIEWS" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "--- List all views ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT viewname FROM pg_views WHERE schemaname = 'public';" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- available_items view (if exists) ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM available_items;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- listed_items view (if exists) ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM listed_items;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- sales_detail view (if exists) ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM sales_detail;" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- revenue_summary view (if exists) ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "SELECT * FROM revenue_summary;" >> "$OUTPUT_FILE" 2>&1

# ============================================================================
# SECTION 4: CONSTRAINTS AND INDEXES
# ============================================================================

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "SECTION 4: CONSTRAINTS AND INDEXES" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "--- All constraints on clothing/shoe/sales tables ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type,
    cc.check_clause
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.check_constraints cc 
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_name IN ('clothing_items', 'shoes_forsale', 'sales', 
                         'clothing_colors', 'clothing_materials', 'clothing_images',
                         'shoe_colors', 'shoe_materials', 'shoe_images')
ORDER BY tc.table_name, tc.constraint_type;
" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- All indexes on clothing/shoe/sales tables ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "
SELECT 
    tablename, 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename IN ('clothing_items', 'shoes_forsale', 'sales',
                    'clothing_colors', 'clothing_materials', 'clothing_images',
                    'shoe_colors', 'shoe_materials', 'shoe_images')
ORDER BY tablename;
" >> "$OUTPUT_FILE" 2>&1

# ============================================================================
# SECTION 5: SEQUENCES
# ============================================================================

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "SECTION 5: SEQUENCES" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "--- All sequences ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "
SELECT sequence_name, last_value 
FROM information_schema.sequences s
JOIN pg_sequences ps ON s.sequence_name = ps.sequencename
WHERE sequence_schema = 'public';
" >> "$OUTPUT_FILE" 2>&1

# ============================================================================
# SECTION 6: FUNCTIONS AND TRIGGERS
# ============================================================================

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "SECTION 6: FUNCTIONS AND TRIGGERS" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "--- All functions ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "
SELECT routine_name, routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public';
" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "--- All triggers ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "
SELECT trigger_name, event_object_table, action_statement 
FROM information_schema.triggers 
WHERE trigger_schema = 'public';
" >> "$OUTPUT_FILE" 2>&1

# ============================================================================
# SECTION 7: SUMMARY COUNTS
# ============================================================================

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "SECTION 7: SUMMARY COUNTS" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "--- Row counts ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "
SELECT 'clothing_items' as table_name, COUNT(*) as row_count FROM clothing_items
UNION ALL SELECT 'clothing_colors', COUNT(*) FROM clothing_colors
UNION ALL SELECT 'clothing_materials', COUNT(*) FROM clothing_materials
UNION ALL SELECT 'clothing_images', COUNT(*) FROM clothing_images
UNION ALL SELECT 'shoes_forsale', COUNT(*) FROM shoes_forsale
UNION ALL SELECT 'shoe_colors', COUNT(*) FROM shoe_colors
UNION ALL SELECT 'shoe_materials', COUNT(*) FROM shoe_materials
UNION ALL SELECT 'shoe_images', COUNT(*) FROM shoe_images
UNION ALL SELECT 'sales', COUNT(*) FROM sales
ORDER BY table_name;
" >> "$OUTPUT_FILE" 2>&1

# ============================================================================
# SECTION 8: FULL JOINED DATA
# ============================================================================

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "SECTION 8: FULL JOINED DATA (CLOTHING)" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "--- Clothing items with all related data ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "
SELECT 
    ci.*,
    STRING_AGG(DISTINCT cc.color, ', ') as colors,
    STRING_AGG(DISTINCT cm.material, ', ') as materials,
    STRING_AGG(DISTINCT cimg.filename, ', ') as image_files
FROM clothing_items ci
LEFT JOIN clothing_colors cc ON ci.id = cc.item_id
LEFT JOIN clothing_materials cm ON ci.id = cm.item_id
LEFT JOIN clothing_images cimg ON ci.id = cimg.item_id
GROUP BY ci.id;
" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "SECTION 9: FULL JOINED DATA (SHOES)" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "--- Shoes with all related data ---" >> "$OUTPUT_FILE"
psql -U postgres -d mythos -c "
SELECT 
    s.*,
    STRING_AGG(DISTINCT sc.color, ', ') as colors,
    STRING_AGG(DISTINCT sm.material, ', ') as materials,
    STRING_AGG(DISTINCT si.filename, ', ') as image_files
FROM shoes_forsale s
LEFT JOIN shoe_colors sc ON s.id = sc.shoe_id
LEFT JOIN shoe_materials sm ON s.id = sm.shoe_id
LEFT JOIN shoe_images si ON s.id = si.shoe_id
GROUP BY s.id;
" >> "$OUTPUT_FILE" 2>&1

# ============================================================================
# DONE
# ============================================================================

echo "" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"
echo "END OF DIAGNOSTIC REPORT" >> "$OUTPUT_FILE"
echo "============================================================================" >> "$OUTPUT_FILE"

echo ""
echo "Diagnostic complete!"
echo "Output saved to: $OUTPUT_FILE"
echo ""
echo "To view: cat $OUTPUT_FILE"
echo "To copy: cat $OUTPUT_FILE | xclip -selection clipboard"
echo ""
