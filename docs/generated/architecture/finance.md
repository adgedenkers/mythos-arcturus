## finance
The finance component processes and analyzes financial data, including bank transactions, bills, and credit card statements, to generate categorized insights, match expenses to bills, and produce user-facing reports for financial oversight.

**Key files and structure**  
Organized into ingestion (`importer.py`, `parsers.py`), matching (`bill_matcher.py`), categorization (`categorizer.py`), and reporting (`report_generator.py`, `reports.py`). Database migrations (`migration_0051_credit_cards.sql`, `migration_add_csv_columns.sql`) manage schema evolution. Critical data artifacts include `2026-01-30_financial_status.md` (sample report) and `report_20260206.html` (output).

**Data flow**  
External data (bank APIs, CSVs) → `importer.py` → `parsers.py` (validation/normalization) → `bill_matcher.py` (bill-transaction matching) → `categorizer.py` (expense classification) → `post_import_analyzer.py` (insights) → `report_generator.py` (HTML/markdown output).

**Dependencies and integration points**  
- **Database**: PostgreSQL (via migrations, transaction storage)  
- **External**: Bank APIs (via `link_bank*.py` for connection setup)  
- **Integration**: Outputs reports to main Mythos UI; inputs via `importer.py` (CSV/API)  

**Known issues**  
- Technical debt: Duplicate bank linking logic in `link_bank.py` and `link_bank2.py` (refactoring pending).  
- Data artifact: Future-dated report file `2026-01-30_financial_status.md` (likely placeholder).
