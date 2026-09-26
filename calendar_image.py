
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Constants for calendar dimensions/layout
WIDTH = 1400
HEIGHT = 600
HEADER_HEIGHT = 60
DAY_WIDTH = WIDTH // 7
PADDING = 10
LINE_SPACING = 18
TASK_SPACING = 16

# Constants for text wrapping
CHARS_PER_LINE = 20
MAX_TASK_LINES_PER_DAY = 22

# Constants for monthly calendar
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_ROW_HEIGHT = 130
MONTH_HEADER_HEIGHT = 40
MONTH_TITLE_HEIGHT = 50
MONTH_CHARS_PER_LINE = 25
MONTH_MAX_TASK_LINES = 5

# Colors for each day of the week
DAY_COLORS = {
    "Monday": "#FFD6D6",
    "Tuesday": "#FFE3C2",
    "Wednesday": "#FFF6C2",
    "Thursday": "#D6F5D9",
    "Friday": "#D6E6FF",
    "Saturday": "#CABFFA",
    "Sunday": "#FFD6EC",
}

# ** WEEK IMAGE **
# Build a 7 column grid with day names and dates, return a PIL Image object
def draw_week_grid(calendar_data):
    # Create initial canvas, white background
    image = Image.new("RGB", (WIDTH, HEIGHT), color="white")
    # Initialize pen object
    draw = ImageDraw.Draw(image)

    # Load a font for the text, set to default if not found
    try:
        font_day_name = ImageFont.truetype("verdana.ttf", 22)
        font_date = ImageFont.truetype("verdana.ttf", 12)
        font_task = ImageFont.truetype("verdana.ttf", 14)
    except IOError:
        font_day_name = font_date = font_task = ImageFont.load_default()


    for i, day in enumerate(calendar_data):
        x_start = i * DAY_WIDTH
        x_end = x_start + DAY_WIDTH
        column_center = x_start + DAY_WIDTH // 2

        # Colored headers
        color = DAY_COLORS.get(day['day_name'], "#FFFFFF")
        draw.rectangle([x_start, 0, x_end, HEADER_HEIGHT], fill=color)

        # Day name (centered in columns)
        day_name = day["day_name"]
        name_bbox = draw.textbbox((0, 0), day_name, font=font_day_name)
        name_width = name_bbox[2] - name_bbox[0]
        draw.text((column_center - name_width // 2, 5), day_name, fill="black", font=font_day_name)

        # Date (centered in columns below day name)
        date_text = day["date"].strftime("%Y-%m-%d")
        date_bbox = draw.textbbox((0, 0), date_text, font=font_date)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text((column_center - date_width / 2, 34), date_text, fill="black", font=font_date)

        # Outer box for day columns
        draw.rectangle([x_start, 0, x_end, HEIGHT], outline="#CCCCCC", width=1)


        # List of tasks for each day
        y = HEADER_HEIGHT + 15 # Height for first task
        lines_drawn = 0
        total_tasks = len(day["tasks"])
        tasks_displayed = 0

        for task in day["tasks"]:
            wrapped_lines = textwrap.wrap(f"- {task.text}", width=CHARS_PER_LINE)

            if lines_drawn + len(wrapped_lines) > MAX_TASK_LINES_PER_DAY:
                break

            for line in wrapped_lines:
                draw.text((x_start + PADDING, y), line, fill="black", font=font_task)
                y += LINE_SPACING
                lines_drawn += 1

            y += TASK_SPACING
            tasks_displayed += 1

        # If there are more tasks that can't be displayed, add a "+N more" line
        if tasks_displayed < total_tasks:
            remaining = total_tasks - tasks_displayed
            draw.text((x_start + PADDING, y), f"+{remaining} more", fill="#888888", font=font_task)
        
    return image


# ** MONTH IMAGE **
# Build a 7-column grid for a full calendar month
# Includes day numbers, task previews, and blank cells for days before the first and last day of the month
def draw_month_grid(calendar_data, month_label):
    first_date = calendar_data[0]["date"]
    leading_blanks = first_date.weekday()
    total_cells = leading_blanks + len(calendar_data)
    num_rows = -(-total_cells // 7)

    height = MONTH_TITLE_HEIGHT + MONTH_HEADER_HEIGHT + (num_rows * MONTH_ROW_HEIGHT)
    image = Image.new("RGB", (WIDTH, height), color="white")
    draw = ImageDraw.Draw(image)

    try:
        font_title = ImageFont.truetype("verdana.ttf", 24)
        font_header = ImageFont.truetype("verdana.ttf", 14)
        font_day_num = ImageFont.truetype("verdana.ttf", 14)
        font_task = ImageFont.truetype("verdana.ttf", 11)
    except IOError:
        font_title = font_header = font_day_num = font_task = ImageFont.load_default()

    # Title (month + year), centered
    title_bbox = draw.textbbox((0, 0), month_label, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((WIDTH - title_width) / 2, 10), month_label, fill="black", font=font_title)

    # Header row
    for col, day_name in enumerate(DAY_NAMES):
        x_start = col * DAY_WIDTH
        color = DAY_COLORS.get(day_name, "#EEEEEE")
        draw.rectangle([x_start, MONTH_TITLE_HEIGHT, x_start + DAY_WIDTH, MONTH_TITLE_HEIGHT + MONTH_HEADER_HEIGHT], fill=color)
        draw.text((x_start + PADDING, MONTH_TITLE_HEIGHT + 10), day_name, fill="black", font=font_header)

    # Flat list of cells (leading blanks + real days)
    cells = [None] * leading_blanks + calendar_data

    grid_top = MONTH_TITLE_HEIGHT + MONTH_HEADER_HEIGHT

    for i, day in enumerate(cells):
        row = i // 7
        col = i % 7
        x_start = col * DAY_WIDTH
        y_start = grid_top + (row * MONTH_ROW_HEIGHT)

        draw.rectangle([x_start, y_start, x_start + DAY_WIDTH, y_start + MONTH_ROW_HEIGHT], outline="#CCCCCC", width=1)

        # Continue past blank cells
        if day is None:
            continue

        # Day numbers
        draw.text((x_start + PADDING, y_start + 5), str(day["date"].day), fill="black", font=font_day_num)

        # Tasks (capped lower than week since individual cells are smaller)
        y = y_start + 25
        lines_drawn = 0
        tasks_shown = 0
        total_tasks = len(day["tasks"])

        for task in day["tasks"]:
            wrapped_lines = textwrap.wrap(f"- {task.text}", width=MONTH_CHARS_PER_LINE)
            if lines_drawn + len(wrapped_lines) > MONTH_MAX_TASK_LINES:
                break
            for line in wrapped_lines:
                draw.text((x_start + PADDING, y), line, fill="black", font=font_task)
                y += 14
                lines_drawn += 1
            tasks_shown += 1

        if tasks_shown < total_tasks:
            remaining = total_tasks - tasks_shown
            draw.text((x_start + PADDING, y), f"+{remaining} more", fill="#888888", font=font_task)

    return image
