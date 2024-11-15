import sqlite3
import csv

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('quest_data.db')
cursor = conn.cursor()

# Update the `CREATE TABLE` statement to include the `difficulty` column
cursor.execute('''
CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_name TEXT NOT NULL,
    points INTEGER,
    scorer TEXT,
    proof TEXT,
    difficulty TEXT  -- New column for difficulty level
)
''')
conn.commit()

# Function to add a quest to the SQLite database
def add_quest(quest_name: str, points: int, scorer: str, proof: str, difficulty: str) -> None:
    cursor.execute('''
    INSERT INTO quests (quest_name, points, scorer, proof, difficulty)
    VALUES (?, ?, ?, ?, ?)
    ''', (quest_name, points, scorer, proof, difficulty))
    conn.commit()

# Function to import quests from a CSV file into SQLite
def import_from_csv(file_path: str) -> None:
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Parse each row's values based on the new columns
            quest_name = row.get('Quests', '').strip()  # Column name should match CSV
            points = row.get('Points', '0').strip()  # Default to '0' if missing
            scorer = row.get('Scorer', '').strip() or "Unclaimed"
            proof = row.get('Proof', '').strip() or "N/A"
            difficulty = row.get('Difficulty', '').strip() or "Unknown"  # Default if missing

            # Try to parse points as an integer, defaulting to 0 if not a valid integer
            try:
                points = int(points)
            except ValueError:
                points = 0  # Default to 0 if parsing fails

            # Insert the quest into the database with difficulty
            add_quest(quest_name, points, scorer, proof, difficulty)

        print("Data imported successfully from CSV.")

# Function to fetch all quests from SQLite
def get_quests():
    cursor.execute('SELECT id, quest_name, points, scorer, proof, difficulty FROM quests')
    return cursor.fetchall()  # Fetch all rows from the table

# Function to append a user to the scorer column
def append_scorer(quest_id: int, user_name: str) -> str:
    try:
        # Get the current scorers for the quest
        cursor.execute('SELECT scorer FROM quests WHERE id = ?', (quest_id,))
        row = cursor.fetchone()
        if not row:
            return f"Quest ID {quest_id} not found."

        current_scorers = row[0] if row[0] else ""
        
        # Split the current scorers into a list and remove "Unclaimed" if present
        scorers_list = [s.strip() for s in current_scorers.split(",") if s.strip() and s.strip().lower() != "unclaimed"]
        
        # Append the user to the scorer list if not already present
        if user_name not in scorers_list:
            scorers_list.append(user_name)
            updated_scorers = ",".join(scorers_list)
            
            # Update the scorer list in the database
            cursor.execute('''
            UPDATE quests
            SET scorer = ?
            WHERE id = ?
            ''', (updated_scorers, quest_id))
            conn.commit()
            
            return f"{user_name} successfully added as a scorer for quest ID {quest_id}."
        else:
            return f"{user_name} is already a scorer for quest ID {quest_id}."
    except sqlite3.Error as e:
        return f"An error occurred while updating the scorer: {e}"

# Function to submit proof for a quest in SQLite
def submit_proof(quest_id: int, user_name: str, proof_link: str) -> str:
    try:
        cursor.execute('''
        UPDATE quests
        SET scorer = ?, proof = ?
        WHERE id = ?
        ''', (user_name, proof_link, quest_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return f"Quest ID {quest_id} not found."
        return f"Proof submitted successfully for quest ID {quest_id}."
    except sqlite3.Error as e:
        return f"An error occurred while submitting proof: {e}"