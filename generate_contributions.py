import subprocess
from datetime import date, timedelta
from collections import Counter


OUTPUT = "contribution-graph.svg"

WEEKS = 53

CELL_SIZE = 12
CELL_GAP = 3

LEFT_MARGIN = 35
TOP_MARGIN = 35
BOTTOM_MARGIN = 35

MONTH_LABEL_HEIGHT = 20
DAY_LABEL_WIDTH = 30


# --------------------------------------------------
# Get git commits
# --------------------------------------------------

def get_commits():
    result = subprocess.run(
        [
            "git",
            "log",
            "--all",
            "--format=%ad",
            "--date=short",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.splitlines()


# --------------------------------------------------
# Count commits per day
# --------------------------------------------------

def build_commit_data():

    commits = get_commits()

    counter = Counter()

    for commit_date in commits:

        try:
            parsed = date.fromisoformat(commit_date)
            counter[parsed] += 1

        except ValueError:
            pass

    return counter


# --------------------------------------------------
# Get level
# --------------------------------------------------

def get_level(count):

    if count == 0:
        return 0

    if count == 1:
        return 1

    if count <= 3:
        return 2

    if count <= 6:
        return 3

    return 4


# --------------------------------------------------
# GitHub-like colors
# --------------------------------------------------

COLORS = [
    "#ebedf0",
    "#9be9a8",
    "#40c463",
    "#30a14e",
    "#216e39",
]


# --------------------------------------------------
# Generate SVG
# --------------------------------------------------

def generate_svg(counter):

    today = date.today()

    # Start from Sunday
    start = today - timedelta(
        days=today.weekday() + 1
    )

    # Go back 52 weeks
    start -= timedelta(
        weeks=WEEKS - 1
    )

    total_days = WEEKS * 7

    width = (
        LEFT_MARGIN
        + WEEKS * (CELL_SIZE + CELL_GAP)
    )

    height = (
        TOP_MARGIN
        + 7 * (CELL_SIZE + CELL_GAP)
        + BOTTOM_MARGIN
    )

    svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<style>

.day {{
    font-family: -apple-system, BlinkMacSystemFont,
    "Segoe UI", Arial, sans-serif;

    font-size: 10px;

    fill: #57606a;
}}

.month {{
    font-family: -apple-system, BlinkMacSystemFont,
    "Segoe UI", Arial, sans-serif;

    font-size: 10px;

    fill: #57606a;
}}

.cell {{
    stroke: rgba(27,31,36,0.06);
    stroke-width: 1;
}}

</style>

<text
x="0"
y="12"
font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
font-size="14"
font-weight="600"
fill="#24292f">
Q4-26 Contributions
</text>
'''

    # --------------------------------------------------
    # Day labels
    # --------------------------------------------------

    day_labels = {
        1: "Mon",
        3: "Wed",
        5: "Fri",
    }

    for row, label in day_labels.items():

        y = (
            TOP_MARGIN
            + row * (CELL_SIZE + CELL_GAP)
            + CELL_SIZE - 2
        )

        svg += f'''
<text
class="day"
x="0"
y="{y}">
{label}
</text>
'''

    # --------------------------------------------------
    # Month labels
    # --------------------------------------------------

    previous_month = None

    for week in range(WEEKS):

        week_date = start + timedelta(
            weeks=week
        )

        month = week_date.month

        if month != previous_month:

            x = (
                LEFT_MARGIN
                + week * (CELL_SIZE + CELL_GAP)
            )

            month_name = week_date.strftime("%b")

            svg += f'''
<text
class="month"
x="{x}"
y="{TOP_MARGIN - 10}">
{month_name}
</text>
'''

            previous_month = month

    # --------------------------------------------------
    # Contribution cells
    # --------------------------------------------------

    for week in range(WEEKS):

        for row in range(7):

            current_date = (
                start
                + timedelta(
                    weeks=week,
                    days=row,
                )
            )

            # Don't draw future days
            if current_date > today:
                continue

            count = counter.get(
                current_date,
                0,
            )

            level = get_level(count)

            x = (
                LEFT_MARGIN
                + week * (CELL_SIZE + CELL_GAP)
            )

            y = (
                TOP_MARGIN
                + row * (CELL_SIZE + CELL_GAP)
            )

            color = COLORS[level]

            formatted_date = current_date.strftime(
                "%b %d, %Y"
            )

            commit_text = (
                "commit"
                if count == 1
                else "commits"
            )

            tooltip = (
                f"{formatted_date}: "
                f"{count} {commit_text}"
            )

            svg += f'''
<rect
class="cell"
x="{x}"
y="{y}"
width="{CELL_SIZE}"
height="{CELL_SIZE}"
rx="2"
fill="{color}">

<title>{tooltip}</title>

</rect>
'''

    # --------------------------------------------------
    # Legend
    # --------------------------------------------------

    legend_y = (
        TOP_MARGIN
        + 7 * (CELL_SIZE + CELL_GAP)
        + 10
    )

    svg += f'''
<text
class="day"
x="{LEFT_MARGIN}"
y="{legend_y + 10}">
Less
</text>
'''

    legend_start = LEFT_MARGIN + 30

    for i, color in enumerate(COLORS):

        x = (
            legend_start
            + i * (CELL_SIZE + CELL_GAP)
        )

        svg += f'''
<rect
class="cell"
x="{x}"
y="{legend_y}"
width="{CELL_SIZE}"
height="{CELL_SIZE}"
rx="2"
fill="{color}">
</rect>
'''

    svg += f'''
<text
class="day"
x="{legend_start + 5 * (CELL_SIZE + CELL_GAP) + 5}"
y="{legend_y + 10}">
More
</text>
'''

    svg += "</svg>"

    with open(
        OUTPUT,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(svg)


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    counter = build_commit_data()

    generate_svg(counter)

    print(
        f"✓ Generated {OUTPUT}"
    )