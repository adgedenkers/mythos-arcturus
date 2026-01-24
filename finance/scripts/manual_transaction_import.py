import csv
import psycopg2
import hashlib
import sys
from datetime import datetime
from pathlib import Path

DB_CONFIG = {
    "dbname": "your_database",
    "user": "your_username",
    "password": "your_password",
    "host": "localhost",
    "port": 5432
}

def compute_hash(row):
    key = f"{row['date']}_{row['amount']}_{row['name']}_{row['account_id']}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()

def import_csv(csv_path, account_id, source_file, imported_by="manual"):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        new_rows = []
        hashes = []

        for row in reader:
            hash_id = compute_hash({
                "date": row["Date"],
                "amount": row["Amount"],
                "name": row["Description"],
                "account_id": account_id
            })

            hashes.append(hash_id)
            new_rows.append((
                account_id,
                row["Date"],
                row["Description"],
                row.get("Merchant", row["Description"]),
                row.get("Category", "Uncategorized"),
                row.get("Category", "Uncategorized"),
                row["Amount"],
                "Credit" if float(row["Amount"]) > 0 else "Debit",
                False,
                "",
                source_file,
                imported_by,
                hash_id,
                datetime.now(),
                datetime.now()
            ))

    cursor.execute(
        "SELECT hash_id FROM transactions WHERE hash_id = ANY(%s)",
        (hashes,)
    )
    existing = set(row[0] for row in cursor.fetchall())

    to_insert = [r for r in new_rows if r[-3] not in existing]

    if to_insert:
        cursor.executemany("""
            INSERT INTO transactions (
                account_id, transaction_date, name, merchant_name, category,
                primary_category, amount, type, is_pending, notes,
                source_file, imported_by, hash_id, imported_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, to_insert)
        conn.commit()

    print(f"Inserted {len(to_insert)} new transactions.")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python manual_transaction_import.py <csv_file> <account_id> <source_file_name>")
    else:
        import_csv(sys.argv[1], sys.argv[2], sys.argv[3])
