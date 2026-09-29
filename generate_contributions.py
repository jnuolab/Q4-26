import subprocess
from datetime import datetime, timedelta
from collections import Counter


OUTPUT = "contribution-graph.svg"

DAYS = 365


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


def build_data():
    commits = get_commits()

    counter = Counter()

    for date in commits:
        try:
            datetime.strptime(date, "%Y-%m-%d")
            counter[date] += 1
        except ValueError:
            pass

    today = datetime.today().date()

    data = []

    for i in range(DAYS - 1, -1, -1):
        day = today - timedelta(days=i)

        date = day.strftime("%Y-%m-%d")

        data.append(
            {
                "date": date,
                "count": counter.get(date, 0),
            }
        )

    return data


def get_level(count):
    if count == 0:
        return 0
    elif count == 1:
        return 1
    elif count <= 3:
        return 2
    elif count <= 6:
        return 3
    else:
        return 4


def generate_svg(data):
    cell = 14
    gap = 4

    width = 53 * (cell + gap)
    height = 7 * (cell + gap) + 40

    svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<text
x="0"
y="20"
font-family="Arial"
font-size="14">
Q4-26 Contributions
</text>
'''

    start_date = datetime.strptime(
        data[0]["date"],
        "%Y-%m-%d"
    ).date()

    # Align to Sunday
    start_date -= timedelta(
        days=(start_date.weekday() + 1) % 7
    )

    for item in data:
        date = datetime.strptime(
            item["date"],
            "%Y-%m-%d"
        ).date()

        diff = (date - start_date).days

        column = diff // 7
        row = diff % 7

        x = column * (cell + gap)
        y = row * (cell + gap) + 30

        level = get_level(item["count"])

        classes = [
            "#ebedf0",
            "#9be9a8",
            "#40c463",
            "#30a14e",
            "#216e39",
        ]

        svg += f'''
<rect
x="{x}"
y="{y}"
width="{cell}"
height="{cell}"
rx="2"
fill="{classes[level]}">
<title>{item["date"]}: {item["count"]} commits</title>
</rect>
'''

    svg += "</svg>"

    with open(OUTPUT, "w", encoding="utf-8") as file:
        file.write(svg)


if __name__ == "__main__":
    data = build_data()
    generate_svg(data)

    print(f"Generated {OUTPUT}")
