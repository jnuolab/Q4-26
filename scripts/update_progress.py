from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

PROGRESS_FILE = ROOT / "progress.json"
README_FILE = ROOT / "README.md"
SVG_FILE = ROOT / "progress.svg"

START_MARKER = "<!-- CONTRIBUTION_GRAPH_START -->"
END_MARKER = "<!-- CONTRIBUTION_GRAPH_END -->"


CELL_SIZE = 12
CELL_GAP = 3
CELL_TOTAL = CELL_SIZE + CELL_GAP

LABEL_WIDTH = 32
TOP_MARGIN = 25
LEFT_MARGIN = LABEL_WIDTH

COLORS = {
    0: "#ebedf0",
    1: "#9be9a8",
    2: "#40c463",
    3: "#30a14e",
    4: "#216e39",
}


def load_progress() -> dict:
    if not PROGRESS_FILE.exists():
        return {}

    with PROGRESS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_level(data: dict, current_date: date) -> int:
    item = data.get(current_date.isoformat(), {})

    try:
        level = int(item.get("level", 0))
    except (TypeError, ValueError):
        level = 0

    return max(0, min(4, level))


def get_tasks(data: dict, current_date: date) -> list[str]:
    item = data.get(current_date.isoformat(), {})

    tasks = item.get("tasks", [])

    if not isinstance(tasks, list):
        return []

    return [str(task) for task in tasks]


def build_days(data: dict) -> list[date]:
    today = date.today()

    # Show the previous 364 days + today.
    start = today - timedelta(days=364)

    return [
        start + timedelta(days=index)
        for index in range(365)
    ]


def align_to_sunday(days: list[date]) -> list[date]:
    """
    GitHub-style calendar starts weeks on Sunday.

    Python weekday:
    Monday = 0
    Sunday = 6
    """

    first_day = days[0]

    days_before = (first_day.weekday() + 1) % 7

    start = first_day - timedelta(days=days_before)

    result = []

    current = start

    while current <= days[-1]:
        result.append(current)
        current += timedelta(days=1)

    return result


def escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def month_labels(days: list[date]) -> list[tuple[int, str]]:
    labels = []

    previous_month = None

    for index, current in enumerate(days):
        if current.month != previous_month:
            labels.append(
                (
                    index,
                    current.strftime("%b")
                )
            )

            previous_month = current.month

    return labels


def build_svg(data: dict) -> str:
    days = build_days(data)
    calendar_days = align_to_sunday(days)

    total_days = len(calendar_days)

    weeks = (total_days + 6) // 7

    width = (
        LEFT_MARGIN
        + weeks * CELL_TOTAL
        + 10
    )

    height = (
        TOP_MARGIN
        + 7 * CELL_TOTAL
        + 35
    )

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'role="img">'
    )

    svg.append(
        '<title>Q4-26 daily progress</title>'
    )

    # Month labels
    for index, label in month_labels(calendar_days):

        week_index = index // 7

        x = (
            LEFT_MARGIN
            + week_index * CELL_TOTAL
        )

        svg.append(
            f'<text x="{x}" y="14" '
            f'font-family="Arial, sans-serif" '
            f'font-size="10" '
            f'fill="#57606a">'
            f'{escape_xml(label)}'
            f'</text>'
        )

    # Day labels
    day_labels = [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri"),
    ]

    for row, label in day_labels:

        y = (
            TOP_MARGIN
            + row * CELL_TOTAL
            + 9
        )

        svg.append(
            f'<text x="0" y="{y}" '
            f'font-family="Arial, sans-serif" '
            f'font-size="9" '
            f'fill="#57606a">'
            f'{label}'
            f'</text>'
        )

    # Cells
    for index, current_date in enumerate(calendar_days):

        week = index // 7
        day = index % 7

        x = (
            LEFT_MARGIN
            + week * CELL_TOTAL
        )

        y = (
            TOP_MARGIN
            + day * CELL_TOTAL
        )

        level = get_level(data, current_date)

        color = COLORS[level]

        tasks = get_tasks(data, current_date)

        task_count = len(tasks)

        if current_date > date.today():
            level = 0
            color = COLORS[0]

        tooltip = (
            f"{current_date.isoformat()} "
            f"— {task_count} task(s)"
        )

        svg.append(
            f'<title>{escape_xml(tooltip)}</title>'
        )

        svg.append(
            f'<rect x="{x}" y="{y}" '
            f'width="{CELL_SIZE}" '
            f'height="{CELL_SIZE}" '
            f'rx="2" ry="2" '
            f'fill="{color}"/>'
        )

    svg.append("</svg>")

    return "\n".join(svg)


def update_readme(svg_filename: str) -> None:
    if not README_FILE.exists():
        README_FILE.write_text(
            "# Q4-26\n\n",
            encoding="utf-8"
        )

    readme = README_FILE.read_text(
        encoding="utf-8"
    )

    graph = (
        f"{START_MARKER}\n"
        f"![Q4-26 Daily Progress](./{svg_filename})\n"
        f"{END_MARKER}"
    )

    if (
        START_MARKER in readme
        and END_MARKER in readme
    ):
        start = readme.index(START_MARKER)
        end = (
            readme.index(END_MARKER)
            + len(END_MARKER)
        )

        readme = (
            readme[:start]
            + graph
            + readme[end:]
        )

    else:
        if not readme.endswith("\n"):
            readme += "\n"

        readme += (
            "\n## 📊 Daily Progress\n\n"
            + graph
            + "\n"
        )

    README_FILE.write_text(
        readme,
        encoding="utf-8"
    )


def main() -> None:
    print("Loading progress...")

    data = load_progress()

    print(
        f"Loaded {len(data)} progress day(s)."
    )

    svg = build_svg(data)

    SVG_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print(
        f"Generated: {SVG_FILE}"
    )

    update_readme(
        SVG_FILE.name
    )

    print(
        f"Updated: {README_FILE}"
    )

    print("Done.")


if __name__ == "__main__":
    main()
