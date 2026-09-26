# Lena

Lena is a personalized discord bot assistant for task management and reminders, built with Python and discord.py.

## Features
- Add, list, and remove tasks via slash commands
- Optional due dates, parsed from flexible natural language (e.g. "Friday", "6/18", "tomorrow", "in 3 days")
- `/today` command to view tasks due today and anything overdue
- `/week`, `/nextweek`, `/month`, `/nextmonth` calendar-range views
- `/weekimage` and `/monthimage` — generates visual calendar images (Pillow), with color-coded days and overflow handling to display tasks and their due dates
- Automatic daily digest posted to a dedicated channel each morning, including a personalized greeting and full weather forecast (high, low, conditions)
- `/setname` and `/setlocation` to personalize the daily digest
- `/testdigest` to manually trigger the digest for testing
- Persistent storage using local SQLite, including a settings table for user preferences
- Task data modeled as a `Task` class (instance + static methods for date logic)
- Friendly error handling for invalid input
- Confirmed working cross-platform (Windows and macOS)

## Planned
- Cloud deployment for 24/7 uptime
- Web dashboard (calendar view, task management)
- Improved task removal (by name/reference instead of only list position)
- Better handling for undated tasks so they don't get lost from calendar-style views
- Customized notifications for non-task related things (tracking job listings, news, etc)

## Tech
- Python, discord.py, SQLite, dateparser, Pillow, requests (OpenWeatherMap API)

## Current Setup
> Note: These steps allow you to run your own instance of the bot using the source code. They don't give access to the bot itself or its data.
1. Clone the repo
2. Create a virtual environment and activate
3. pip install -r requirements.txt
4. Create a .env file with:
   - `DISCORD_TOKEN=your_token_here`
   - `DIGEST_CHANNEL_ID=your_channel_id_here` (if desired)
   - `OWM_API_KEY=your_openweathermap_key_here` (if desired, for weather in the daily digest)
5. python bot.py

## Adding Lena to Your Server
> Note: Lena is currently private and in development. Please check back later.
1. Click this invite link: []
2. Select the server you'd like to add Lena to (you'll need "Manage Server" permissions)
3. Review the requested permissions and click "Authorize"
4. Once added, type '/' in any channel Lena can see to view her available commands.
