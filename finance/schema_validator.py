#!/usr/bin/env python3
"""
Mythos Finance - Database Schema Validator
Compares actual database schema against expected schema and generates report.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv('/opt/mythos/.env')

OUTPUT_FILE = '/opt/mythos/finance/schema_report.md'

# Expected schema definition
EXPECTED_SCHEMA = {
    'accounts': {
        'columns': {
            'id': 'integer',
            'bank_name': 'character varying(100)',
            'account_name': 'character varying(255)',
            'account_number': 'character varying(50)',
            'account_type': 'character varying(50)',
            'is_active': 'boolean',
            'notes': 'text',
            'created_at': 'timestamp without time zone',
            'updated_at': 'timestamp without time zone',
        }
    },
    'transactions': {
        'columns': {
            'id': 'integer',
            'account_id': 'integer',
            'transaction_date': 'date',
            'post_date': 'date',
            'description': 'text',
            'original_description': 'text',
            'merchant_name': 'character varying(255)',
            'amount': 'numeric(12,2)',
            'balance': 'numeric(12,2)',
            'category_primary': 'character varying(100)',
            'category_secondary': 'character varying(100)',
            'transaction_type': 'character varying(50)',
            'is_pending': 'boolean',
            'is_recurring': 'boolean',
            'bank_transaction_id': 'character varying(100)',
            'hash_id': 'character varying(64)',
            'source_file': 'character varying(255)',
            'imported_by': 'character varying(100)',
            'notes': 'text',
            'created_at': 'timestamp without time zone',
            'updated_at': 'timestamp without time zone',
        }
    },
    'import_logs': {
        'columns': {
            'id': 'integer',
            'account_id': 'integer',
            'source_file': 'character varying(255)',
            'file_path': 'text',
            'total_rows': 'integer',
            'imported_count': 'integer',
            'skipped_count': 'integer',
            'error_count': 'integer',
            'date_range_start': 'date',
            'date_range_end': 'date',
            'imported_by': 'character varying(100)',
            'imported_at': 'timestamp without time zone',
            'notes': 'text',
        }
    },
    'category_mappings': {
        'columns': {
            'id': 'integer',
            'pattern': 'character varying(255)',
            'pattern_type': 'character varying(20)',
            'category_primary': 'character varying(100)',
            'category_secondary': 'character varying(100)',
            'merchant_name': 'character varying(255)',
            'priority': 'integer',
            'is_active': 'boolean',
            'created_at': 'timestamp without time zone',
        }
    },
    'recurring_bills': {
        'columns': {
            'id': 'integer',
            'account_id': 'integer',
            'merchant_name': 'character varying(255)',
            'expected_amount': 'numeric(12,2)',
            'amount_variance': 'numeric(12,2)',
            'frequency': 'character varying(20)',
            'expected_day': 'integer',
            'category_primary': 'character varying(100)',
            'is_active': 'boolean',
            'notes': 'text',
            'created_at': 'timestamp without time zone',
        }
    },
}


def get_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def get_actual_tables(cur):
    """Get list of all tables in public schema"""
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    return [row['table_name'] for row in cur.fetchall()]


def get_actual_columns(cur, table_name):
    """Get columns for a specific table"""
    cur.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    return cur.fetchall()


def format_data_type(col):
    """Format the full data type string"""
    dtype = col['data_type']
    if col['character_maximum_length']:
        dtype = f"character varying({col['character_maximum_length']})"
    elif col['numeric_precision'] and col['numeric_scale']:
        dtype = f"numeric({col['numeric_precision']},{col['numeric_scale']})"
    return dtype


def get_table_row_count(cur, table_name):
    """Get row count for a table"""
    try:
        cur.execute(f"SELECT COUNT(*) as cnt FROM {table_name}")
        return cur.fetchone()['cnt']
    except:
        return "ERROR"


def get_indexes(cur, table_name):
    """Get indexes for a table"""
    cur.execute("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = %s
        ORDER BY indexname
    """, (table_name,))
    return cur.fetchall()


def generate_report():
    """Generate the full schema comparison report"""
    conn = get_connection()
    cur = conn.cursor()
    
    report = []
    report.append("# Mythos Finance - Database Schema Report")
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Database: {os.getenv('POSTGRES_DB', 'mythos')}")
    report.append("")
    
    # Get actual tables
    actual_tables = get_actual_tables(cur)
    expected_tables = list(EXPECTED_SCHEMA.keys())
    
    # Summary
    report.append("## Summary")
    report.append("")
    report.append(f"| Metric | Count |")
    report.append(f"|--------|-------|")
    report.append(f"| Expected Tables | {len(expected_tables)} |")
    report.append(f"| Actual Tables | {len(actual_tables)} |")
    report.append(f"| Missing Tables | {len(set(expected_tables) - set(actual_tables))} |")
    report.append(f"| Extra Tables | {len(set(actual_tables) - set(expected_tables))} |")
    report.append("")
    
    # Missing tables
    missing_tables = set(expected_tables) - set(actual_tables)
    if missing_tables:
        report.append("## ❌ Missing Tables")
        report.append("")
        for t in sorted(missing_tables):
            report.append(f"- `{t}`")
        report.append("")
    
    # Extra tables (in DB but not expected)
    extra_tables = set(actual_tables) - set(expected_tables)
    if extra_tables:
        report.append("## ℹ️ Extra Tables (not in expected schema)")
        report.append("")
        for t in sorted(extra_tables):
            count = get_table_row_count(cur, t)
            report.append(f"- `{t}` ({count} rows)")
        report.append("")
    
    # Detailed table analysis
    report.append("## Table Details")
    report.append("")
    
    all_issues = []
    
    for table_name in sorted(set(expected_tables) | set(actual_tables)):
        report.append(f"### {table_name}")
        report.append("")
        
        if table_name not in actual_tables:
            report.append("**Status:** ❌ TABLE MISSING")
            report.append("")
            all_issues.append(f"Table `{table_name}` is missing entirely")
            continue
        
        if table_name not in expected_tables:
            report.append("**Status:** ℹ️ Extra table (not in expected schema)")
            actual_cols = get_actual_columns(cur, table_name)
            report.append("")
            report.append("| Column | Type | Nullable | Default |")
            report.append("|--------|------|----------|---------|")
            for col in actual_cols:
                dtype = format_data_type(col)
                report.append(f"| {col['column_name']} | {dtype} | {col['is_nullable']} | {col['column_default'] or '-'} |")
            report.append("")
            continue
        
        # Compare columns
        expected_cols = EXPECTED_SCHEMA[table_name]['columns']
        actual_cols = get_actual_columns(cur, table_name)
        actual_col_dict = {c['column_name']: c for c in actual_cols}
        
        row_count = get_table_row_count(cur, table_name)
        report.append(f"**Rows:** {row_count}")
        report.append("")
        
        missing_cols = set(expected_cols.keys()) - set(actual_col_dict.keys())
        extra_cols = set(actual_col_dict.keys()) - set(expected_cols.keys())
        
        if missing_cols or extra_cols:
            report.append("**Status:** ⚠️ Schema mismatch")
        else:
            report.append("**Status:** ✅ Schema matches")
        report.append("")
        
        if missing_cols:
            report.append("**Missing Columns:**")
            for col in sorted(missing_cols):
                report.append(f"- `{col}` (expected: {expected_cols[col]})")
                all_issues.append(f"Table `{table_name}` missing column `{col}` ({expected_cols[col]})")
            report.append("")
        
        if extra_cols:
            report.append("**Extra Columns (in DB, not expected):**")
            for col in sorted(extra_cols):
                dtype = format_data_type(actual_col_dict[col])
                report.append(f"- `{col}` ({dtype})")
            report.append("")
        
        # Full column comparison table
        report.append("| Column | Expected | Actual | Match |")
        report.append("|--------|----------|--------|-------|")
        
        all_col_names = sorted(set(expected_cols.keys()) | set(actual_col_dict.keys()))
        for col_name in all_col_names:
            expected_type = expected_cols.get(col_name, '-')
            if col_name in actual_col_dict:
                actual_type = format_data_type(actual_col_dict[col_name])
            else:
                actual_type = '❌ MISSING'
            
            if expected_type == '-':
                match = 'ℹ️'
            elif actual_type == '❌ MISSING':
                match = '❌'
            elif expected_type == actual_type:
                match = '✅'
            else:
                match = '⚠️'
                
            report.append(f"| {col_name} | {expected_type} | {actual_type} | {match} |")
        
        report.append("")
        
        # Indexes
        indexes = get_indexes(cur, table_name)
        if indexes:
            report.append("**Indexes:**")
            for idx in indexes:
                report.append(f"- `{idx['indexname']}`")
            report.append("")
    
    # Migration SQL
    if all_issues:
        report.append("## 🔧 Suggested Migration SQL")
        report.append("")
        report.append("Run these commands to fix schema issues:")
        report.append("")
        report.append("```sql")
        
        for table_name in expected_tables:
            if table_name not in actual_tables:
                report.append(f"-- Table {table_name} needs to be created (run full schema.sql)")
                continue
            
            expected_cols = EXPECTED_SCHEMA[table_name]['columns']
            actual_cols = get_actual_columns(cur, table_name)
            actual_col_names = {c['column_name'] for c in actual_cols}
            
            for col_name, col_type in expected_cols.items():
                if col_name not in actual_col_names:
                    # Generate ALTER TABLE statement
                    default = ""
                    if 'boolean' in col_type:
                        default = " DEFAULT false"
                    elif 'timestamp' in col_type:
                        default = " DEFAULT CURRENT_TIMESTAMP"
                    elif 'integer' in col_type and col_name != 'id':
                        default = " DEFAULT 0"
                    
                    report.append(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}{default};")
        
        report.append("```")
        report.append("")
    
    # Write report
    conn.close()
    
    report_text = '\n'.join(report)
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write(report_text)
    
    print(f"Report written to: {OUTPUT_FILE}")
    print(f"\nOpen with: code {OUTPUT_FILE}")
    print("\n" + "=" * 60)
    print("QUICK SUMMARY")
    print("=" * 60)
    
    if all_issues:
        print(f"\n⚠️ Found {len(all_issues)} issue(s):\n")
        for issue in all_issues[:10]:
            print(f"  - {issue}")
        if len(all_issues) > 10:
            print(f"  ... and {len(all_issues) - 10} more (see full report)")
    else:
        print("\n✅ All tables match expected schema!")
    
    return len(all_issues)


if __name__ == "__main__":
    try:
        issues = generate_report()
        sys.exit(0 if issues == 0 else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
