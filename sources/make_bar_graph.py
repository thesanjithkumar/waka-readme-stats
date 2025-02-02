from typing import Dict
from os.path import join, dirname
from json import load

import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from download_manager import DownloadManager


MAX_LANGUAGES = 5


async def build_graph(yearly_data: Dict) -> str:
    """
    Draws graph of lines of code written by user by quarters of years.
    Picks top `MAX_LANGUAGES` languages from each quarter only.

    :param yearly_data: GitHub user yearly data.
    :return: String, path to graph file.
    """
    colors = await DownloadManager.get_remote_yaml("linguist")

    languages_all_loc = dict()
    years = len(yearly_data.keys())
    year_indexes = np.arange(years)

    for i, y in enumerate(sorted(yearly_data.keys())):
        for q in yearly_data[y].keys():
            langs = sorted(yearly_data[y][q].keys(), key=lambda l: yearly_data[y][q][l], reverse=True)[0:MAX_LANGUAGES]

            for lang in langs:
                if lang not in languages_all_loc:
                    languages_all_loc[lang] = np.array([[0] * years] * 4)
                languages_all_loc[lang][q - 1][i] = yearly_data[y][q][lang]

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1.5, 1])

    language_handles = []
    cumulative = np.array([[0] * years] * 4)

    for key, value in languages_all_loc.items():
        color = colors[key]["color"] if colors[key]["color"] is not None else "w"
        language_handles += [mpatches.Patch(color=color, label=key)]

        for quarter in range(4):
            ax.bar(year_indexes + quarter * 0.21, value[quarter], 0.2, bottom=cumulative[quarter], color=color)
            cumulative[quarter] = np.add(cumulative[quarter], value[quarter])

    ax.set_ylabel("LOC added", fontdict=dict(weight="bold"))
    ax.set_xticks(np.array([np.arange(i, i + 0.84, step=0.21) for i in year_indexes]).flatten(), labels=["Q1", "Q2", "Q3", "Q4"] * years)

    sax = ax.secondary_xaxis("top")
    sax.set_xticks(year_indexes + 0.42, labels=sorted(yearly_data.keys()))
    sax.spines["top"].set_visible(False)

    ax.legend(title="Language", handles=language_handles, loc="upper left", bbox_to_anchor=(1, 1), framealpha=0, title_fontproperties=dict(weight="bold"))

    sax.tick_params(axis="both", length=0)
    sax.spines["top"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.ylim(0, 1.05 * np.amax(cumulative))
    plt.savefig("bar_graph.png", bbox_inches="tight")
    plt.close(fig)
    return "bar_graph.png"
