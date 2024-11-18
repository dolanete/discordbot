from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents
from discord.ext import commands
import responses  # Import responses for command handling
import database


# Load token
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Bot setup with command prefix and intents
intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Command to add a quest
@bot.command(name='addquest')
async def add_quest(ctx, *, args: str):
    response = await responses.handle_addquest(args)
    await ctx.send(response)

# Command to list quests
@bot.command(name='listquests')
async def list_quests(ctx):
    response_chunks = responses.handle_listquests()
    for chunk in response_chunks:
        await ctx.send(chunk)

# Command to import quests from a CSV file
@bot.command(name='importcsv')
async def import_csv(ctx):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]  # Use the first attachment
        await responses.import_csv_from_attachment(ctx, attachment)
    else:
        await ctx.send("Please attach a CSV file with the command.")

# Command for users to submit proof for a quest
@bot.command(name='submit')
async def submit_quest(ctx, quest_id: int, link: str):
    try:
        # Get the submitting user's name
        user_name = ctx.author.name

        # Use the append_scorer function from the database module
        result = database.append_scorer_and_proof(quest_id, user_name, link)

        # Send the result of the operation to the Discord channel
        await ctx.send(result)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


# Bot startup event
@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')

# Main entry point
def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
