import sys
from datetime import datetime
from json import loads
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def make_graph(mods: list[tuple[str, datetime]], title: str):
    labels = [m[0] for m in mods]
    dates = [m[1] for m in mods]
    tile_len = len(dates) // 5
    tile_in = [tile_len * -1]
    while tile_in[-1] != 1:
        if tile_in[-1] < 0:
            tile_in.append(tile_in[-1] * -1)
        else:
            tile_in.append((tile_in[-1] - 1) * -1)
    levels = np.tile(tile_in,
                     int(np.ceil(len(dates) / tile_len)))[:len(dates)]
    fig, ax = plt.subplots(figsize=(len(dates), len(dates) // 2))
    ax.set(title=title)
    ax.vlines(dates, 0, levels, color="tab:red")

    ax.plot(dates, np.zeros_like(dates), "-o", color='k', markerfacecolor='w')
    ax.autoscale(enable=True, tight=True)

    for d, l, r in zip(dates, levels, labels):
        ax.annotate(r, xy=(d, l), xytext=(-3, np.sign(1) * 3), textcoords="offset points",
                    horizontalalignment='left', verticalalignment="bottom" if l > 0 else "top", backgroundcolor='white', bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="red", lw=2))

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    ax.yaxis.set_visible(False)
    ax.spines[['left', 'top', 'right']].set_visible(False)

    ax.margins(y=1)

    plt.tight_layout()
    plt.savefig(f"{title}.png", format='png')
    # plt.show(aspect='auto')


def main(file_path: Path, release_filter: str):
    parsed_json = loads(file_path.read_text())
    if release_filter == 'release' or release_filter == "no-nh" or release_filter == 'only-nh':
        releases = parsed_json['releases']
    elif release_filter == 'alpha':
        releases = parsed_json['alphaReleases']
    else:
        releases = parsed_json['releases'] + parsed_json['alphaReleases']

    if release_filter == 'no-nh':
        releases = filter(lambda m: 'parent' not in m.keys() or m['parent'] != 'xen.NewHorizons', releases)
    elif release_filter == 'only-nh':
        releases = filter(lambda m: 'parent' in m.keys() and m['parent'] == 'xen.NewHorizons', releases)

    mods = [(m['name'], datetime.strptime(m['firstReleaseDate'], "%Y-%m-%dT%H:%M:%SZ")) for m in releases]
    mods.sort(key=lambda m: m[1])
    make_graph(mods, f"OW Mods Timeline ({release_filter})")


if __name__ == '__main__':
    try:
        filepath = Path(sys.argv[1])
        if len(sys.argv) >= 3:
            mod_filter = sys.argv[2]
        else:
            mod_filter = 'all'
        if filepath.exists():
            main(filepath, mod_filter)
        else:
            print(f"File: {str(filepath.as_posix())} not found")
            sys.exit(1)
    except IndexError:
        print("Usage: main.py DB_FILE_PATH [Filter ('all', 'release', 'alpha', 'only-nh', or 'no-nh')]")
        sys.exit(1)



