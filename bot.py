# Note: for command names to be typed by users, snake_case is avoided for convenience.
# Command names are instead written in lowercase with no spaces, e.g. /addtask, /listtasks, etc.


# ====================================
#               SETUP
# ====================================

import os
import discord
import database
import dateparser
import calendar
import calendar_image
import weather

from discord.ext import commands
from discord.ext import tasks
from datetime import time, date, datetime, timedelta
from dotenv import load_dotenv
from task import Task
from zoneinfo import ZoneInfo

# Currently set to PST for personal use
# NOTE: IF YOU DOWNLOADED THIS CODE FOR PERSONAL USE, CHANGE TO YOUR LOCAL TIMEZONE HERE
LOCAL_TZ = ZoneInfo("America/Los_Angeles")

# Pull bot token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DIGEST_CHANNEL_ID"))

# Match permissions set in Discord Developer Portal
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance with command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize database
database.init_db()
database.init_settings_table()


# ====================================
#            BASE EVENTS
# ====================================

# Sanity check, ensure bot is connected to Discord
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash command(s).")
    daily_digest.start()


# ====================================
#           HELPER METHODS
# ====================================

# Return today's date in the designated, local timezone rather than the eventual host server's own local time
# Goal here is consistency after deployment. Avoid defaulting to UTC or timezones that are unintended.
# NOTE: If this bot is changed in the future to work for various users, date configuration should be tied to Discord account
def get_local_today():
    return datetime.now(LOCAL_TZ).date()

# Build the due date message summary used by /today and daily digest
def build_today_message():
    today = get_local_today()
    tasks_list = database.get_tasks()
    due_today = [task for task in tasks_list if task.is_due_today(today)]
    overdue = [task for task in tasks_list if task.is_overdue(today)]

    if not due_today and not overdue:
        return "Nothing is due today and nothing is overdue. You're all caught up!"

    lines = []
    if overdue:
        lines.append("**Overdue:**")
        for task in overdue:
            lines.append(f"- {task.text} (was due {task.format_due_date()})")
        lines.append("")
    if due_today:
        lines.append("**Due today:**")
        for task in due_today:
            lines.append(f"- {task.text}")

    return "\n".join(lines)

# Build a summary grouping tasks by individual days between start_date and end_date (inclusive)
def build_range_message(start_date, end_date, title):
    tasks = database.get_tasks_due_between(start_date.isoformat(), end_date.isoformat())

    if not tasks:
        return f"Nothing due in {title.lower()}."

    # Group tasks by day
    grouped = {}
    for task in tasks:
        # Dictionary comprised of keys = due_date, values = list of tasks due on that date)
        grouped.setdefault(task.due_date, []).append(task)

    lines = [f"**{title}:**"]
    for due_date in sorted(grouped.keys()):
        display_date = Task.format_date_string(due_date)
        lines.append(f"**{display_date}**")
        for task in grouped[due_date]:
            lines.append(f" - {task.text}")

    return "\n".join(lines)

def build_digest_message():
    location = database.get_setting("location")
    name = database.get_setting("name")

    greeting = f"Good morning, {name}! :)" if name else "Good morning! :)"
    if location:
        forecast = weather.get_forecast(location)
        if forecast:
            greeting += f" Today's forecast in {location}: a high of {forecast['high']}°F and a low of {forecast['low']}°F with {forecast['description']}."

    return greeting + "\n\n" + build_today_message()

# ====================================
#          SCHEDULED TASKS
# ====================================

# Daily message sent at 9 AM
@tasks.loop(time=time(hour=9, minute=0))
async def daily_digest():
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(build_digest_message())

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
    message = build_today_message()
    await interaction.response.send_message(message)

# Show tasks due over the current calendar month
# (e.g. if used on September 15th, it will show tasks due between September 1st and September 30th)
# Usage: /month
@bot.tree.command(name="month", description="Show tasks due over the current calendar month")
async def month(interaction: discord.Interaction):
    today = get_local_today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    end = date(today.year, today.month, last_day)
    message = build_range_message(today, end, "This Month")
    await interaction.response.send_message(message)

# Show tasks due over the current week
# (e.g. if used on Wednesday, it will show tasks due between Monday and Sunday of the current week)
# Usage: /week
@bot.tree.command(name="week", description="Show tasks due over the current week")
async def week(interaction: discord.Interaction):
    today = get_local_today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    message = build_range_message(start, end, "This Week")
    await interaction.response.send_message(message)

# Show tasks due over the next 7 days (starting from today)
# Usage: /nextweek
@bot.tree.command(name="nextweek", description="Show tasks due over the next 7 days")
async def nextweek(interaction: discord.Interaction):
    today = get_local_today()
    end = today + timedelta(days=6)
    message = build_range_message(today, end, "Next 7 Days")
    await interaction.response.send_message(message)

# Show tasks due over the next 31 days (starting from today)
# Usage: /nextmonth
@bot.tree.command(name="nextmonth", description="Show tasks due over the next 31 days")
async def nextmonth(interaction: discord.Interaction):
    today = get_local_today()
    end = today + timedelta(days=30)
    message = build_range_message(today, end, "Next 31 Days")
    await interaction.response.send_message(message)

# Show a visual calendar of tasks due over the current week
# Usage: /weekimage
@bot.tree.command(name="weekimage", description="Show a visual calendar of tasks due over the current week")
async def weekimage(interaction: discord.Interaction):
    today = get_local_today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    data = database.build_calendar_data(start, end)

    # Save the image to a temporary file
    image = calendar_image.draw_week_grid(data)
    image.save("week_temp.png")
    
    # Send the image file as a response to the user
    await interaction.response.send_message(file=discord.File("week_temp.png"))

# Show a visual calendar of tasks due over the current month
# Usage: /monthimage
@bot.tree.command(name="monthimage", description="Show a visual calendar of tasks due over the current month")
async def monthimage(interaction: discord.Interaction):
    today = get_local_today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    start = date(today.year, today.month, 1)
    end = date(today.year, today.month, last_day)
    data = database.build_calendar_data(start, end)

    month_label = today.strftime("%B %Y")
    image = calendar_image.draw_month_grid(data, month_label)
    image.save("month_temp.png")

    await interaction.response.send_message(file=discord.File("month_temp.png"))

# Set the user's name for messaging purposes (e.g. "Good morning, <name>!")
# Usage: /setname <name>
@bot.tree.command(name="setname", description="Set your name for personalized messages")
@discord.app_commands.describe(name="Your name/alias")
async def setname(interaction: discord.Interaction, name: str):
    database.set_setting("name", name)
    await interaction.response.send_message(f"Name set to: {name}")

# Set the user's location for weather information
# Usage: /setlocation <city_name>
@bot.tree.command(name="setlocation", description="Set your location for weather in daily digest")
@discord.app_commands.describe(location="City name (example: Seattle)")
async def setlocation(interaction: discord.Interaction, location: str):
    database.set_setting("location", location)
    await interaction.response.send_message(f"Location set to: {location}")

# Test command to trigger digest message anytime
# Usage: /testdigest
@bot.tree.command(name="testdigest", description="Manually trigger the daily digest message")
async def testdigest(interaction: discord.Interaction):
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(build_digest_message())
    # Setting ephemeral to true means only user who used command can see the response
    await interaction.response.send_message("Digest message sent.", ephemeral=True)

# Run bot with token
bot.run(TOKEN)
