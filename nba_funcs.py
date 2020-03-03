import espn_scraper as espn
import csv
import matplotlib.pyplot as plt
import os.path
from matplotlib.offsetbox import AnnotationBbox
from matplotlib import animation
import numpy as np

plt.rcParams.update({'font.size': 22})

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
        # Assists!
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
        time_for_log = (float(quarter) - 1) * 12 + (12.0 - min_frac)
    else:
        min_frac = float(time)
        time_for_log = (float(quarter) - 1) * 12 + (12.0 - min_frac/60)

    if time_for_log < 0:
        print("HERE")
        print(play_dict)
        print(quarter)
        print(min_frac)
    return time_for_log


def plot_player(quarter_time, running_total, name, target, teamColor, image):

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xticks([1, 2, 3, 4], minor=False)
    ax.xaxis.grid(True, which='major')

    plt.plot(quarter_time, running_total, color=teamColor, linewidth=2)
    plt.hlines(target, 0, 4, colors='red', linewidth=2, linestyles='--')
    plt.xlabel("Time, Quarters")
    plt.ylabel("PRA Total")
    plt.title("PRA Total for " + name)
    plt.grid(axis='y')
    plt.xlim([0, 4])
    plt.ylim([0, max(running_total) + 5])
    if image:
        ab = AnnotationBbox(image, (quarter_time[-1], running_total[-1]), xycoords='data', frameon=False)
        ax.add_artist(ab)
    fig.savefig(name + ".png", format='png', dpi=1200)
    ax.remove()
    plt.clf()
    plt.cla()
    plt.close()


def plot_player_both(player_dict, name, target, teamColor, image, flag, gid):
    running_total = []
    total = 0
    quarter_time = []
    for pra in player_dict[name][0]:
        total = pra + total
        running_total.append(total)
    for time in player_dict[name][1]:
        quarter_time.append(time/12)
    if flag:
        plot_player(quarter_time, running_total, name, target, teamColor, image)
    else:
        plot_animate(quarter_time, running_total, image, target, teamColor, name, gid)


def plot_animate(clock, running_total, image, target, teamColor, name, gid):
    fig2 = plt.figure(figsize=(16, 9), dpi=240)
    ax2 = plt.axes(xlim=(0, 4), ylim=(0, running_total[-1]*1.5))
    ax2.set_xticks([1, 2, 3, 4], minor=False)
    ax2.xaxis.grid(True, which='major')

    ims = []
    xdata, ydata = [], []
    clock_smoothed = [0]
    running_total_smoothed = [0]
    plt.rcParams['animation.ffmpeg_path'] = './FFmpeg/bin/ffmpeg.exe'
    for i in range(len(clock)):
        if i == 0:
            clock_smoothed.append(clock[i])
            running_total_smoothed.append(running_total[i])
        else:
            dt_quart = clock[i] - clock[i-1]
            ticks = int(round(dt_quart * 30))
            clock_smoothed.extend(np.linspace(clock[i - 1], clock[i], ticks))
            running_total_smoothed.extend(np.linspace(running_total[i - 1], running_total[i], ticks))

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
        ims.append(ims[-1])
    plt.xlabel("Time, Quarters")
    plt.ylabel("PRA Total")
    plt.title("PRA Total for " + name)
    plt.grid(axis='y')

    anim = animation.ArtistAnimation(fig2, ims, interval=1, repeat=False, blit=True)
    writer = animation.FFMpegWriter(fps=20, codec="libx264", bitrate=10000, extra_args=['-pix_fmt', 'yuv420p'], metadata=None)
    filepath = "./data/" + name + "/"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    fullpath = filepath +  name + "_" + str(gid) + '.mp4'
    anim.save(fullpath, dpi=240, writer=writer)


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




