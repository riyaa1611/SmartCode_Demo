import sqlite3
import os

# Database file path
db_file = 'dev.db'

if not os.path.exists(db_file):
    print("No database file found. Initializing new one via main app startup is recommended if this is a fresh install.")
    # If no DB exists, models.py will create tables with new schema automatically on startup.
    exit(0)

print(f"Updating database: {db_file}")

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def add_column_if_not_exists(table, column, type_def):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")
        print(f"Added column {column} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print(f"Column {column} already exists in {table}")
        else:
            print(f"Error adding {column} to {table}: {e}")

# Update reviews table
add_column_if_not_exists('reviews', 'summary', 'TEXT')
add_column_if_not_exists('reviews', 'share_token', 'TEXT')
add_column_if_not_exists('reviews', 'share_password', 'TEXT')
add_column_if_not_exists('reviews', 'share_expires_at', 'TIMESTAMP')

# Update findings table
add_column_if_not_exists('findings', 'code_snippet', 'TEXT')
add_column_if_not_exists('findings', 'suggestion', 'TEXT')

conn.commit()
conn.close()
print("Database schema update completed.")
