import sqlite3


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


# Return list of (id, task_text) tuples from the database
def get_tasks():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_text FROM tasks ORDER BY id")
    results = cursor.fetchall()
    conn.close()
    return results


# Remove task given a numbered position from the database
def remove_task_by_position(position):
    tasks = get_tasks()
    if position < 1 or position > len(tasks):
        return None  # Invalid position
    task_id, task_text = tasks[position - 1]
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,)) # Note: ? is a placeholder for the task_id variable, prevents SQL injection
    conn.commit()
    conn.close()

    return task_text # Return the removed task text for confirmation
