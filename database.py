import sqlite3
from datetime import timedelta

from task import Task


DB_FILE = "tasks.db"


def init_db():
    # Open (or create, if not existing) database file in project folder
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Executes actual SQL command, in this case, creating the table (if it doesn't exist)
    # Does nothing if table already exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_text TEXT NOT NULL,
            due_date TEXT
        )
    """)
    # SQLite "save" step, changes only persist through sessions if committed
    conn.commit()
    # Release database resources by closing connection to database file
    conn.close()


# Add a new task to the database
def add_task(task_text, due_date=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task_text, due_date) VALUES (?, ?)", (task_text, due_date))
    conn.commit()
    conn.close()


# Return list of Task objects, built from database rows
def get_tasks():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_text, due_date FROM tasks ORDER BY id")
    results = cursor.fetchall()
    conn.close()

    return [Task(task_id, text, due_date) for task_id, text, due_date in results]


# Remove task given a numbered position from the database
def remove_task_by_position(position):
    tasks = get_tasks()
    if position < 1 or position > len(tasks):
        return None  # Invalid position
    task = tasks[position - 1]
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task.id,)) # Note: ? is a placeholder for the task_id variable, prevents SQL injection
    conn.commit()
    conn.close()

    return task.text # Return the removed task text for confirmation

# Return Task objects with due_date between start_date and end_date (inclusive)
def get_tasks_due_between(start_date, end_date):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_text, due_date FROM tasks WHERE due_date BETWEEN ? and ? ORDER BY due_date",
                   (start_date, end_date))

    results = cursor.fetchall()
    conn.close()

    return [Task(task_id, text, due_date) for task_id, text, due_date in results]

# Return a list of dicts (1 per day), each with date and list of tasks (can be empty)
def build_calendar_data(start_date, end_date):
    tasks = get_tasks_due_between(start_date.isoformat(), end_date.isoformat())

    # Group tasks by due date
    grouped = {}
    for task in tasks:
        grouped.setdefault(task.due_date, []).append(task)

    # Build one entry per day in the range, even if no tasks exist
    calendar_data = []
    current_date = start_date
    while current_date <= end_date:
        day_tasks = grouped.get(current_date.isoformat(), [])
        calendar_data.append({
            "date": current_date,
            "day_name": current_date.strftime("%A"),
            "tasks": day_tasks
        })
        current_date += timedelta(days=1)

    return calendar_data

# Create settings table if it doesn't already exist
# Stores simple key-value pairs (e.g. "location" -> "Seattle"), separate from tasks
def init_settings_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

# Save a setting to the settings table (insert or update)
def set_setting(key, value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# Retrieve a setting's value by its key, or None if it hasn't been set
def get_setting(key):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
