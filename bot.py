import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

# Pull bot token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Match permissions set in Discord Developer Portal
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance with command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Sanity check, ensure bot is connected to Discord
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

# Ping command to test responsiveness (responds to !ping in server with "Pong!")
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Run bot with token
bot.run(TOKEN)
