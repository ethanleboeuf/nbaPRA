import espn_scraper as espn
import csv
import matplotlib.pyplot as plt
import os.path
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import animation
import numpy as np

plt.rcParams['grid.color'] = '#000000'
plt.rcParams.update({'font.size': 22})
COLOR = '#069c47'
plt.rcParams['text.color'] = COLOR
plt.rcParams['axes.labelcolor'] = COLOR
plt.rcParams['xtick.color'] = COLOR
plt.rcParams['ytick.color'] = COLOR
plt.rcParams['figure.facecolor'] = '#000000'
plt.rcParams['animation.ffmpeg_path'] = './FFmpeg/bin/ffmpeg.exe'


def get_last_n_games(n, name):
    dir = "./data/" + name + "/"
    files = []
    for file in os.listdir(dir):
        if file.endswith(".txt"):
            files.append(dir + file)
    files.sort(reverse=True)

    pra, targets = [], []
    n = max(n, len(files))
    for i in range(n):
        currfile = open(files[i])
        line = currfile.readlines()
        pra_target = line[0].split(",")
        pra.append(float(pra_target[0]))
        targets.append(float(pra_target[1]))
        currfile.close()

    return pra, targets, n


def player_bar_graph(n, pra, targets, name):
    image = get_image(name, 0.6)
    x = []
    h = []
    lab = [" "]
    over = "#069c47"
    under = "#FF0000"
    c = []
    for i in range(n):
        x.append(i+1)
        val = pra[i] / targets[i]
        h.append(val)
        lab.append(str(i))
        if val > 1:
            c.append(over)
        elif val < 1:
            c.append(under)
        else:
            c.append("#000000")
    fig, ax = plt.subplots(figsize=(n+5, 10))
    plt.bar(x, h, 0.5, color=c)
    plt.xlim([n+1, 0])
    # plt.ylim([0, max(3.5, max(h)*2)])
    plt.ylim([0, 5])
    locs, labels = plt.xticks()
    plt.xticks(np.arange(len(lab)), lab, fontsize=16)
    plt.hlines(1, 0, n+1, color="red", linestyles="--", linewidth=2)
    ab = AnnotationBbox(image, (1.5, 3), xycoords='data', frameon=False)
    ax.add_artist(ab)
    plt.title("Last " + str(n) + " game(s) for " + name)
    plt.ylabel("Assists / Target Value")
    plt.xlabel("Games Ago")

    filepath = "./data/" + name + "/"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    fullpath = filepath +  name + "_Last" + str(n) + "games" + '.png'
    fig.savefig(fullpath, format='png', dpi=800, facecolor=fig.get_facecolor())


def get_image(name, zoom):
    image = plt.imread("Player Pics/" + name + ".png")
    image = OffsetImage(image, zoom=zoom)
    return image
