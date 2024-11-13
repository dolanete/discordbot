import csv
import os
import database

async def handle_addquest(args: str) -> str:
    # Split the arguments by commas
    try:
        quest_details = args.split(",")

        if len(quest_details) == 5:
            quest_name = quest_details[0].strip()
            points = int(quest_details[1].strip())
            scorer = quest_details[2].strip()
            proof = quest_details[3].strip()
            valid = quest_details[4].strip().lower() in ("true", "1", "yes")

            # Add quest with boolean `valid` field
            database.add_quest(quest_name, points, scorer, proof, valid)
            return f'Quest "{quest_name}" added with {points} points by {scorer}. Valid: {"Yes" if valid else "No"}'
        else:
            return "Invalid command format. Use: !addquest quest_name, points, scorer, proof, valid"
    except ValueError:
        return "Invalid command format. Ensure points is a number and format is correct."

def handle_listquests() -> str:
    quests = database.get_quests()
    return "Quest List:\n" + "\n".join(
        [f"{q[0]}: {q[1]}, Points: {q[2]}, Scorer: {q[3]}, Proof: {q[4]}" for q in quests]
    )

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
                scorer = row.get('Scorer', '').strip() or "Unknown"
                proof = row.get('Proof', '').strip() or "N/A"
                valid = row.get('Valid', 'false').strip().lower() in ("true", "1", "yes")

                # Try to parse points as an integer, defaulting to 0 if not a valid integer
                try:
                    points = int(points)
                except ValueError:
                    points = 0  # Default to 0 if parsing fails

                # Add the quest to the database
                database.add_quest(quest_name, points, scorer, proof, valid)

            await ctx.send("Data imported successfully from CSV.")
    except Exception as e:
        await ctx.send(f"An error occurred while importing data: {e}")
    finally:
        # Clean up by deleting the temporary CSV file
        os.remove(csv_path)
