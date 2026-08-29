# Lena

Lena is a personalized discord bot assistant for task management and reminders, built with Python and discord.py.

## Features (so far)
- Add, list, and remove tasks via Disord commands
- Optional due date assignment to tasks
- Persistent storage using SQLite
- Descriptive error handling for invalid inputs
- (In progress) migration to Discord's native slash commands

## Planned
- Scheduling/Reminders (daily task digest)
- Cloud deployment for 24/7 uptime
- Full slash command support

## Tech
- Python, discord.py, SQLite

## Current Setup
1. Clone the repo
2. Create a virtual environment and activate
3. pip install -r requirements.txt
4. Create a .env file with DISCORD_TOKEN=your_token_here
5. python bot.py