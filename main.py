from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Attachment
from discord.ext import commands
import responses  # Import responses for command handling

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
    response = responses.handle_listquests()
    await ctx.send(response)

# Command to import quests from a CSV file
@bot.command(name='importcsv')
async def import_csv(ctx):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]  # Use the first attachment
        await responses.import_csv_from_attachment(ctx, attachment)
    else:
        await ctx.send("Please attach a CSV file with the command.")

# Bot startup event
@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')

# Main entry point
def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
