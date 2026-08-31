from datetime import date, datetime

class Task:
    def __init__(self, task_id, text, due_date=None):
        self.id = task_id
        self.text = text
        self.due_date = due_date # Store in YYYY-MM-DD format, or None (if not given)

    # Return true if the task is overdue, false otherwise
    def is_overdue(self):
        # If no due date, task is never overdue
        if self.due_date is None:
            return False
        due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
        return due < date.today()

    # Return true if task is due today, false otherwise
    def is_due_today(self):
        if self.due_date is None:
            return False
        due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
        return due == date.today()

    # User-friendly version of due date
    def format_due_date(self):
        return Task.format_date_string(self.due_date)

    # Static version of format method, for use without necessitating a Task instance
    @staticmethod
    def format_date_string(date_str):
        if date_str is None:
            return ""
        due = datetime.strptime(date_str, "%Y-%m-%d")
        return due.strftime("%A, %B %d, %Y")

