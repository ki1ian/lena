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
> Note: These steps allow you to run your own instance of the bot using the source code. They don't give access to the bot itself or its data.
1. Clone the repo
2. Create a virtual environment and activate
3. pip install -r requirements.txt
4. Create a .env file with DISCORD_TOKEN=your_token_here
5. python bot.py

## Adding Lena to Your Server
> Note: Lena is currently private and in development. Please check back later.
1. Click this invite link: []
2. Select the server you'd like to add Lena to (you'll need "Manage Server" permissions)
3. Review the requested permissions and click "Authorize"
4. Once added, type '/' in any channel Lena can see to view her available commands.