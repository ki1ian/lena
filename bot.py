# Note: for command names to be typed by users, snake_case is avoided for convenience.
# Command names are instead written in lowercase with no spaces, e.g. !addtask, !listtasks, etc.

# ====================================
#               SETUP
# ====================================

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


# ====================================
#              EVENTS
# ====================================

# Sanity check, ensure bot is connected to Discord
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


# ====================================
#              COMMANDS
# ====================================

# Ping command to test responsiveness (responds to !ping in server with "Pong!")
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Temporary in-memory task storage for testing (resets when Lena restarts)
tasks = []

# Append new tasks (capture all text into 1 argument using *)
# Usage: !addtask <task_text>
@bot.command()
async def addtask(ctx, *, task_text):
    tasks.append(task_text)
    await ctx.send(f"Task added: {task_text}")

# Display all tasks currently stored
# Usage: !listtasks
@bot.command()
async def listtasks(ctx):
    if not tasks:
        await ctx.send("No tasks exist.")
        return
    # Loop through tasks, number them, combine into 1 message -> send to Discord
    task_lines = [f"{i + 1}. {task}" for i, task in enumerate(tasks)]
    await ctx.send("Tasks:\n" + "\n".join(task_lines))

# Remove a task from the list by its number (1-indexed)
# Usage: !removetask <task_number>
@bot.command()
async def removetask(ctx, task_number: int): # type hint, ensure number given is an int
    if task_number < 1 or task_number > len(tasks):
        await ctx.send("Invalid task number (out of range). Use !listtasks to see valid numbers.")
        return
    removed = tasks.pop(task_number - 1)
    await ctx.send(f"Task removed: {removed}")

# Run bot with token
bot.run(TOKEN)
