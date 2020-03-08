import espn_scraper as espn
import csv
import matplotlib.pyplot as plt
import os.path
from matplotlib.offsetbox import AnnotationBbox
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

def get_player_dict(csv_name):
    player_dict = dict()
    with open(csv_name, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    for player in data:
        player_dict[player[0]] = [[], []]
    return player_dict


def fill_player_dict(game_id, player_dict):
    url = espn.get_game_url("playbyplay", "nba", game_id)
    print(url)
    data = espn.get_url(url)
    team_names = [data["gamepackageJSON"]["boxscore"]["teams"][0]["team"]["shortDisplayName"], data["gamepackageJSON"]["boxscore"]["teams"][1]["team"]["shortDisplayName"]]

    for play in data["gamepackageJSON"]["plays"]:
        play_text = play["text"].split()
        if len(play_text) < 2:
            continue

        name = play_text[0] + " " + play_text[1]
        if name in player_dict:
            if len(play_text) > 3:
                # Rebounds!
                if play_text[3] == "rebound":
                    player_dict[name][0].append(1)

                    player_dict[name][1].append(get_time(play))
            if play["scoringPlay"]:
                # Scoring play!
                player_dict[name][0].append(play["scoreValue"])
                player_dict[name][1].append(get_time(play))
        #Assists!
        if play_text[-1] == "assists)":
            name_assist = play_text[-3][1:] + " " + play_text[-2]
            if name_assist in player_dict:
                player_dict[name_assist][0].append(1)

                player_dict[name_assist][1].append(get_time(play))

    print(get_time(data["gamepackageJSON"]["plays"][-1]))
    return player_dict, team_names


def get_time(play_dict):
    quarter = play_dict["period"]["displayValue"][0]
    time = play_dict["clock"]["displayValue"]
    if ":" in time:
        min_sec = time.split(":")
        min_frac = float(min_sec[0]) + float(min_sec[1]) / 60
        if quarter == "O":
            quarter = 5

        time_for_log = (float(quarter) - 1) * 12 + (12.0 - min_frac)
    else:
        min_frac = float(time)
        if quarter == "O":
            quarter = 5
        time_for_log = (float(quarter) - 1) * 12 + (12.0 - min_frac/60)

    if time_for_log < 0:
        print("HERE")
        print(play_dict)
        print(quarter)
        print(min_frac)
    return time_for_log


def plot_player(clock_smoothed, running_total_smoothed, name, target, teamColor, image, gid):

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xticks([1, 2, 3, 4], minor=False)
    ax.xaxis.grid(True, which='major')

    plt.plot(clock_smoothed, running_total_smoothed, color=teamColor, linewidth=2)
    plt.hlines(target, 0, 4, colors='red', linewidth=2, linestyles='--')
    plt.xlabel("Time, Quarters")
    plt.ylabel("PRA Total")
    plt.title("PRA Total for " + name)
    plt.grid(axis='y')
    plt.xlim([0, 4])
    plt.ylim([0, max(running_total_smoothed) + 5])
    if image:
        if running_total_smoothed[-1] >= target:
            ab = AnnotationBbox(image, (clock_smoothed[-1], running_total_smoothed[-1] * (1.25)),
                                 xycoords='data', frameon=False)
        else:
            ab = AnnotationBbox(image, (clock_smoothed[-1], running_total_smoothed[-1] * (0.75)),
                                 xycoords='data', frameon=False)
        ax.add_artist(ab)
    filepath = "./data/" + name + "/"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    fullpath = filepath +  name + "_" + str(gid) + '.png'
    fig.savefig(fullpath, format='png', dpi=1200, facecolor=fig.get_facecolor())
    ax.remove()
    plt.clf()
    plt.cla()
    plt.close()


def process_player(player_dict, name, target, teamColor, image, flag, gid):
    running_total = []
    total = 0
    quarter_time = []
    prev_total = 0
    for pra in player_dict[name][0]:
        total = pra + total
        running_total.append(prev_total)
        running_total.append(total)
        prev_total = total
    for time in player_dict[name][1]:
        quarter_time.append(time/12)
        quarter_time.append(time/12)

    clock_smoothed, running_total_smoothed = smooth_data(quarter_time, running_total)
    if flag == 1:
        plot_player(clock_smoothed, running_total_smoothed, name, target, teamColor, image, gid)
    elif flag == 0:
        plot_animate(clock_smoothed, running_total_smoothed, image, target, teamColor, name, gid)
    write_ind_to_txt(running_total[-1], target, name, gid)


def plot_animate(clock_smoothed, running_total_smoothed, image, target, teamColor, name, gid):
    fig2 = plt.figure(figsize=(16, 9), dpi=240)
    ax2 = plt.axes(xlim=(0, 4), ylim=(0, running_total_smoothed[-1]*1.5))
    ax2.set_xticks([1, 2, 3, 4], minor=False)
    ax2.xaxis.grid(True, which='major')
    ims = []
    xdata, ydata = [], []
    ln1 = []
    ln2 = []
    ln3 = []
    for i in range(len(clock_smoothed)):
        xdata.append(clock_smoothed[i])
        ydata.append(running_total_smoothed[i])

        ln1, = plt.plot(xdata, ydata, color=teamColor, lw=2)
        ab2 = AnnotationBbox(image, (clock_smoothed[i], running_total_smoothed[i]), xycoords='data', frameon=False)
        ln3 = plt.hlines(target, 0, 4, colors='red', linestyles="--")
        if image:
            ln2 = ax2.add_artist(ab2)
            ims.append([ln1, ln2, ln3])
        else:
            ims.append([ln1, ln3])
    for i in range(40):
        if image:
            if running_total_smoothed[-1] >= target:
                ab2 = AnnotationBbox(image, (clock_smoothed[-1], running_total_smoothed[-1] * (1 + 0.25/(40-i))), xycoords='data', frameon=False)

            else:
                ab2 = AnnotationBbox(image, (clock_smoothed[-1], running_total_smoothed[-1] * (1 - 0.25/(40-i))), xycoords='data', frameon=False)

            ln2 = ax2.add_artist(ab2)
            ims.append([ln1, ln2, ln3])
        else:
            ims.append(ims[-1])
    for i in range(40):
        ims.append(ims[-1])

    plt.xlabel("Time, Quarters")
    plt.ylabel("PRA Total")
    plt.title("PRA Total for " + name)
    plt.grid(axis='y')
    fig2.patch.set_facecolor('black')
    anim = animation.ArtistAnimation(fig2, ims, interval=1, repeat=False, blit=True)
    writer = animation.FFMpegWriter(fps=20, codec="libx264", bitrate=10000, extra_args=['-pix_fmt', 'yuv420p'], metadata=None)
    filepath = "./data/" + name + "/"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    fullpath = filepath +  name + "_" + str(gid) + '.mp4'
    anim.save(fullpath, dpi=240, writer=writer, savefig_kwargs={'facecolor':'black'})


def write_player_dict_to_csv(player_dict, directory, filename):

    fp = os.path.join(directory, filename)
    if not os.path.isdir(directory):
        os.mkdir(directory)
    with open(fp, 'w') as f:
        for key in player_dict.keys():
            if player_dict[key][0]:
                f.write("%s," % key)
                total = 0
                for val in player_dict[key][0]:
                    total = val + total
                    f.write("%f," % total)
                f.write("\n")
                first_pass = 1
                for time in player_dict[key][1]:
                    if first_pass:
                        f.write("%s," % " ")
                        first_pass = 0
                    f.write("%f," % time)
                f.write("\n")


def get_team_colors(team_data):
    team_colors = dict()
    for team in team_data:
        team_colors[team["team"]["shortDisplayName"]] = "#" + team["team"]["color"]
    return team_colors


def smooth_data(clock, running_total):
    clock_smoothed = [0]
    running_total_smoothed = [0]
    for i in range(len(clock)):
        if i == 0:
            clock_smoothed.append(clock[i])
            running_total_smoothed.append(running_total[i])
        else:
            dt_quart = clock[i] - clock[i-1]
            ticks = max(int(round(dt_quart * 30)), 2)
            clock_smoothed.extend(np.linspace(clock[i - 1], clock[i], ticks))
            running_total_smoothed.extend(np.linspace(running_total[i - 1], running_total[i], ticks))
    return clock_smoothed, running_total_smoothed


def write_ind_to_txt(pra, target, name, gid):
    filepath = "./data/" + name + "/"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    file1 = open(filepath + name + "_" + str(gid) + ".txt", "w")
    file1.write(str(pra) + "," + str(target))
    file1.close()




