# Note: for command names to be typed by users, snake_case is avoided for convenience.
# Command names are instead written in lowercase with no spaces, e.g. /addtask, /listtasks, etc.


# ====================================
#               SETUP
# ====================================

import os
import discord
import database
import dateparser

from discord.ext import commands
from dotenv import load_dotenv
from task import Task

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
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash command(s).")


# ====================================
#              COMMANDS
# ====================================

# Ping command to test responsiveness (responds to /ping in server with "Pong!")
@bot.tree.command(name="ping", description="Check if Lena is responsive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


# Append new tasks given 2 fields: <task_text> and <due_date>
# Usage: /addtask <task_text> <due_date>
@bot.tree.command(name="addtask", description="Add a new task to your schedule")
@discord.app_commands.describe(task_text="What is the task?", due_date="Optional due date (e.g. Friday, 6/18, Tomorrow)")
async def addtask(interaction: discord.Interaction, task_text: str, due_date: str = None):
    parsed_date = None
    if due_date:
        # If a due date exists, Lena should be able to interpret user input with flexibility
        # For example: whether they say "6/18", "June 18", "June 18th", it's stored as the same date.
        # Additionally, we prefer dates from the future. So if the user inputs "Friday", and the current day
        # is Friday, Lena interprets that as the upcoming friday, not "today".
        parsed = dateparser.parse(due_date, settings={'PREFER_DATES_FROM': 'future'})
        if parsed is None:
            await interaction.response.send_message(f"Could not parse the date '{due_date}'. Try something like 'Friday', '6/18', or 'Tomorrow'.")
            return
        parsed_date = parsed.date().isoformat() # Convert to YYYY-MM-DD format for DB storage

    database.add_task(task_text, parsed_date)

    if parsed_date:
        display_date = Task.format_date_string(parsed_date)
        await interaction.response.send_message(f"Task added: {task_text} (Due: {display_date})")
    else:
        await interaction.response.send_message(f"Task added: {task_text}")
    

# Display all tasks current stored in database
# Usage: /listtasks
@bot.tree.command(name="listtasks", description="List all active tasks in your schedule")
async def listtasks(interaction: discord.Interaction):
    tasks = database.get_tasks()
    if not tasks:
        await interaction.response.send_message("No tasks exist.")
        return
    task_lines = []
    for i, task in enumerate(tasks):
        if task.due_date:
            task_lines.append(f"{i + 1}. {task.text} (Due: {task.format_due_date()})")
        else:
            task_lines.append(f"{i + 1}. {task.text}")
    await interaction.response.send_message("Tasks:\n" + "\n".join(task_lines))


# Remove a task from the list given its assigned number
# Usage: /removetask <task_number>
@bot.tree.command(name="removetask", description="Remove a task from your schedule by its number")
@discord.app_commands.describe(task_number="The task number shown in /listtasks")
async def removetask(interaction: discord.Interaction, task_number: int):
    removed = database.remove_task_by_position(task_number)
    if removed is None:
        await interaction.response.send_message(f"Invalid task number: {task_number}. Use /listtasks to see valid numbers.")
        return
    await interaction.response.send_message(f"Task removed: {removed}")


# Show tasks due today, and flag any tasks that are overdue
# Usage: /today
@bot.tree.command(name="today", description="Show tasks that are due today (and anything marked as overdue)")
async def today(interaction: discord.Interaction):
    tasks = database.get_tasks()

    due_today = [task for task in tasks if task.is_due_today()]
    overdue = [task for task in tasks if task.is_overdue()]

    if not due_today and not overdue:
        await interaction.response.send_message("Nothing is due today or overdue. You're all caught up!")
        return

    lines = []

    if overdue:
        lines.append("**Overdue:**")
        for task in overdue:
            lines.append(f"- {task.text} (was due {task.format_due_date()})")
        lines.append("") # spacing between overdue and due

    if due_today:
        lines.append("**Due today:**")
        for task in due_today:
            lines.append(f"- {task.text}")

    await interaction.response.send_message("\n".join(lines))

# Run bot with token
bot.run(TOKEN)
