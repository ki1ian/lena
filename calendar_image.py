
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Calendar dimensions/layout constants
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