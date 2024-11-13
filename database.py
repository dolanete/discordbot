# database.py
import sqlite3
import csv

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('quest_data.db')
cursor = conn.cursor()

# Modify the table to include the `valid` column with boolean-like values
cursor.execute('''
CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_name TEXT NOT NULL,
    points INTEGER,
    scorer TEXT,
    proof TEXT,
    valid INTEGER DEFAULT 1  -- Boolean equivalent: 1 for True, 0 for False
)
''')
conn.commit()

# Function to add a quest with a boolean `valid` field
def add_quest(quest_name: str, points: int, scorer: str, proof: str, valid: bool = True) -> None:
    cursor.execute('''
    INSERT INTO quests (quest_name, points, scorer, proof, valid)
    VALUES (?, ?, ?, ?, ?)
    ''', (quest_name, points, scorer, proof, int(valid)))  # Convert boolean to 1 or 0
    conn.commit()

def import_from_csv(file_path: str) -> None:
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)  # Using DictReader to handle headers
        for row in reader:
            # Parse each row's values and convert valid to a boolean (1 or 0)
            quest_name = row['quest_name'].strip()
            points = int(row['points'].strip())
            scorer = row['scorer'].strip()
            proof = row['proof'].strip()
            valid = row['valid'].strip().lower() in ("true", "1", "yes")

            # Insert the quest into the database
            add_quest(quest_name, points, scorer, proof, valid)

        print("Data imported successfully from CSV.")

# Function to fetch all quests, converting `valid` back to boolean
def get_quests():
    cursor.execute('SELECT id, quest_name, points, scorer, proof, valid FROM quests')
    return [(q[0], q[1], q[2], q[3], q[4], bool(q[5])) for q in cursor.fetchall()]  # Convert integer to boolean

