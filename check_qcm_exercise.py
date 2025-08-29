import sqlite3
import json

# Connect to the database
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# First, check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Available tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check if there's an exercise table (might be named differently)
for table in tables:
    table_name = table[0]
    if 'exercise' in table_name.lower():
        print(f"\nChecking table: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Try to find QCM exercises
        cursor.execute(f'SELECT * FROM {table_name} WHERE title LIKE "%Test image QCM%" OR title LIKE "%QCM%"')
        results = cursor.fetchall()
        if results:
            print(f"\nFound {len(results)} exercise(s):")
            for result in results:
                print(f"  Exercise: {result}")

conn.close()
