# Lena

Lena is a personalized discord bot assistant for task management and reminders, built with Python and discord.py.

## Features (so far)
- Add, list, and remove tasks via Disord commands
- Optional due date assignment to tasks, parsed from flexible natural language (e.g. "Friday", "6/18", "14 days ago", "today")
- '/today' command to view tasks due today and anything overdue
- Automatic daily summary of due/overdue tasks posted to a dedicated channel each morning
- Persistent storage using SQLite
- Descriptive error handling for invalid inputs
- Task data modeled as a 'Task' class (instance + static methods for  date logic)

## Planned
- Expanded scheduling (weekly/monthly views, editable messages)
- Cloud deployment for 24/7 uptime
- Potential future modules: fitness tracking, designated alerts

## Tech
- Python, discord.py, SQLite, dateparser

## Current Setup
> Note: These steps allow you to run your own instance of the bot using the source code. They don't give access to the bot itself or its data.
1. Clone the repo
2. Create a virtual environment and activate
3. pip install -r requirements.txt
4. Create a .env file with DISCORD_TOKEN=your_token_here, DIGEST_CHANNEL_ID=your_channel_id_here (if desired)
5. python bot.py

## Adding Lena to Your Server
> Note: Lena is currently private and in development. Please check back later.
1. Click this invite link: []
2. Select the server you'd like to add Lena to (you'll need "Manage Server" permissions)
3. Review the requested permissions and click "Authorize"
4. Once added, type '/' in any channel Lena can see to view her available commands.