import csv
import os
import database

async def handle_addquest(args: str) -> str:
    # Split the arguments by commas
    try:
        quest_details = args.split(",")

        if len(quest_details) == 5:  # Now expects only five parameters
            quest_name = quest_details[0].strip()
            points = int(quest_details[1].strip())
            scorer = quest_details[2].strip()
            proof = quest_details[3].strip()
            difficulty = quest_details[4].strip()  # Difficulty column instead of valid

            # Add quest to the database
            database.add_quest(quest_name, points, scorer, proof, difficulty)
            return f'Quest "{quest_name}" added with {points} points by {scorer}. Difficulty: {difficulty}'
        else:
            return "Invalid command format. Use: !addquest quest_name, points, scorer, proof, difficulty"
    except ValueError:
        return "Invalid command format. Ensure points is a number and format is correct."

def handle_listquests() -> list:
    quests = database.get_quests()
    quest_list = [
        f"{q[1]} (ID: {q[0]}), Points: {q[2]}, Scorer: {q[3]}, Proof: {q[4]}, Difficulty: {q[5]}"
        for q in quests
    ]
    
    # Combine quests into chunks of up to 2000 characters
    response_chunks = []
    chunk = ""
    for quest in quest_list:
        if len(chunk) + len(quest) + 1 > 2000:  # Add 1 for the newline character
            response_chunks.append(chunk)
            chunk = ""
        chunk += quest + "\n"
    
    # Add the last chunk if it's not empty
    if chunk:
        response_chunks.append(chunk)
    
    return response_chunks

async def import_csv_from_attachment(ctx, attachment):
    if not attachment.filename.endswith('.csv'):
        await ctx.send("Please attach a valid CSV file.")
        return

    # Save the attachment to a temporary file path
    csv_path = f"./{attachment.filename}"
    await attachment.save(csv_path)
    await ctx.send(f"File '{attachment.filename}' received. Importing data...")

    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            # Use DictReader to automatically handle headers
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Safely extract each field, using default values for missing fields
                quest_name = row.get('Quests', '').strip()
                points = row.get('Points', '0').strip()  # Default to '0' if missing
                scorer = row.get('Scorer', '').strip() or "Unclaimed"
                proof = row.get('Proof', '').strip() or "N/A"
                difficulty = row.get('Difficulty', '').strip()  # New Difficulty column

                # Try to parse points as an integer, defaulting to 0 if not a valid integer
                try:
                    points = int(points)
                except ValueError:
                    points = 0  # Default to 0 if parsing fails

                # Add the quest to the database
                database.add_quest(quest_name, points, scorer, proof, difficulty)

            await ctx.send("Data imported successfully from CSV.")
    except Exception as e:
        await ctx.send(f"An error occurred while importing data: {e}")
    finally:
        # Clean up by deleting the temporary CSV file
        os.remove(csv_path)

def handle_submit(quest_id: int, user_name: str, proof_link: str) -> str:
    return database.submit_proof(quest_id, user_name, proof_link)
