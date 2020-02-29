import espn_scraper as espn
import csv
import matplotlib.pyplot as plt
import numpy

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

    for play in data["gamepackageJSON"]["plays"]:
        play_text = play["text"].split()
        name = play_text[0] + " " + play_text[1]
        if name in player_dict:
            # Rebounds!
            if play_text[2] == "defensive" or play_text[2] == "offensive":
                player_dict[name][0].append(1)

                player_dict[name][1].append(get_time(play))
            if play["scoringPlay"]:
                player_dict[name][0].append(play["scoreValue"])
                player_dict[name][1].append(get_time(play))
        # Assists!
        if play_text[-1] == "assists)":
            name_assist = play_text[-3][1:] + " " + play_text[-2]
            if name_assist in player_dict:
                player_dict[name_assist][0].append(1)

                player_dict[name_assist][1].append(get_time(play))

    print(get_time(data["gamepackageJSON"]["plays"][-1]))
    return player_dict


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


def plot_player(player_dict, name, target):
    running_total = []
    total = 0
    quarter_time = []
    for pra in player_dict[name][0]:
        total = pra + total
        running_total.append(total)
    for time in player_dict[name][1]:
        quarter_time.append(time/12)

    fig, ax = plt.subplots()
    ax.set_xticks([1, 2, 3, 4], minor=False)
    ax.xaxis.grid(True, which='major')

    plt.plot(quarter_time, running_total,linewidth=2)
    plt.hlines(target, 0, 4, colors='red', linewidth=2)
    plt.xlabel("Time, Quarters")
    plt.ylabel("PRA Total")
    plt.title("PRA Total for " + name)
    plt.grid(axis='y')
    plt.xlim([0, 4])
    plt.ylim([0, target + 10])
    plt.show()


