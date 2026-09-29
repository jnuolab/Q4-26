import json
import math
import re
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "progress.json"
PROGRESS_DIR = ROOT / "progress"

LEVEL_COLORS = {
    0: "#ebedf0",
    1: "#9be9a8",
    2: "#40c463",
    3: "#30a14e",
    4: "#216e39",
}


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_activities(data):
    activities = set()

    for day_data in data.values():
        activities.update(day_data.keys())

    return sorted(activities)


def safe_filename(name):
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9_-]+", "-", name)
    return name.strip("-")


def activity_title(activity):
    return activity.replace("-", " ").title()


def get_level(data, activity, current_date):
    day_data = data.get(current_date.isoformat(), {})
    return int(day_data.get(activity, 0))


def generate_svg(data, activity, output_file):
    today = date.today()

    # Show approximately one year.
    start_date = today - timedelta(days=364)

    # Align to Sunday.
    start_date -= timedelta(days=(start_date.weekday() + 1) % 7)

    end_date = today

    cell_size = 12
    cell_gap = 3
    step = cell_size + cell_gap

    weeks = math.ceil(
        ((end_date - start_date).days + 1) / 7
    )

    left_margin = 35
    top_margin = 30

    width = left_margin + weeks * step + 10
    height = top_margin + 7 * step + 10

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    svg.append(
        f'<rect width="{width}" height="{height}" fill="white"/>'
    )

    # Weekday labels
    weekdays = {
        1: "Mon",
        3: "Wed",
        5: "Fri",
    }

    for row, label in weekdays.items():
        y = top_margin + row * step + 10

        svg.append(
            f'<text x="0" y="{y}" '
            f'font-family="Arial" font-size="10" '
            f'fill="#57606a">{label}</text>'
        )

    # Cells
    current = start_date

    while current <= end_date:
        days_from_start = (current - start_date).days

        week = days_from_start // 7
        row = days_from_start % 7

        x = left_margin + week * step
        y = top_margin + row * step

        level = get_level(data, activity, current)
        color = LEVEL_COLORS.get(level, LEVEL_COLORS[0])

        title = (
            f"{activity_title(activity)} — "
            f"{current.isoformat()} — Level {level}"
        )

        svg.append(
            f'<rect x="{x}" y="{y}" '
            f'width="{cell_size}" height="{cell_size}" '
            f'rx="2" ry="2" fill="{color}">'
            f'<title>{title}</title>'
            f'</rect>'
        )

        current += timedelta(days=1)

    svg.append("</svg>")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def generate_all(data):
    activities = get_activities(data)

    print(f"Found {len(activities)} activities.")

    for activity in activities:
        filename = safe_filename(activity)

        output_file = PROGRESS_DIR / f"{filename}.svg"

        generate_svg(
            data,
            activity,
            output_file
        )

        print(f"Generated: {output_file}")


def main():
    print("Loading progress.json...")

    data = load_data()

    generate_all(data)

    print("Done.")


if __name__ == "__main__":
    main()
