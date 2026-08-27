# Note: for command names to be typed by users, snake_case is avoided for convenience.
# Command names are instead written in lowercase with no spaces, e.g. !addtask, !listtasks, etc.


# ====================================
#               SETUP
# ====================================

import os
import discord
import database

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

# Initialize database
database.init_db()


# ====================================
#            BASE EVENTS
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

# Append new tasks (capture all text into 1 argument using *)
# Usage: !addtask <task_text>
@bot.command()
async def addtask(ctx, *, task_text):
    database.add_task(task_text)
    await ctx.send(f"Task added: {task_text}")

# Display all tasks currently stored
# Usage: !listtasks
@bot.command()
async def listtasks(ctx):
    tasks = database.get_tasks()
    if not tasks:
        await ctx.send("No tasks exist.")
        return
    # Loop through tasks, number them, combine into 1 message -> send to Discord
    task_lines = [f"{i + 1}. {text}" for i, (task_id, text) in enumerate(tasks)]
    await ctx.send("Tasks:\n" + "\n".join(task_lines))

# Remove a task from the list by its number (1-indexed)
# Usage: !removetask <task_number>
@bot.command()
async def removetask(ctx, task_number: int): # type hint, ensure number given is an int
    removed = database.remove_task_by_position(task_number)
    if removed is None:
        await ctx.send(f"Invalid task number: {task_number}. Use !listtasks to see valid task numbers.")
        return
    await ctx.send(f"Task removed: {removed}")


# ====================================
#            ERROR HANDLING
# ====================================

# Catch errors from any command and reply with a helpful message
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument. Usage: `!{ctx.command} {ctx.command.signature}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Invalid argument. Usage: `!{ctx.command} {ctx.command.signature}`")
    elif isinstance(error, commands.CommandNotFound):
        pass # Ignore unrecognized commands to avoid spamming channel with error messages
    else:
        await ctx.send("An unexpected error occurred. Please try again later.")
        # Log error to terminal for debugging
        print(f"Unhandled error: {error}")
        raise error 
    

# Run bot with token
bot.run(TOKEN)
