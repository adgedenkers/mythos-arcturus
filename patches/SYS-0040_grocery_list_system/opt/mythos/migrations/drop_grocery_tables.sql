-- Drop orphaned grocery_* tables (replaced by existing shopping_* system)
DROP TABLE IF EXISTS grocery_items CASCADE;
DROP TABLE IF EXISTS grocery_lists CASCADE;
DROP TABLE IF EXISTS grocery_aisles CASCADE;
