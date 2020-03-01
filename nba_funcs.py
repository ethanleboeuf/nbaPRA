import espn_scraper as espn
import csv
import matplotlib.pyplot as plt
import os.path


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


def plot_player(player_dict, name, target, teamColors, team):
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

    plt.plot(quarter_time, running_total, color=teamColors[team], linewidth=2)
    plt.hlines(target, 0, 4, colors='red', linewidth=2)
    plt.xlabel("Time, Quarters")
    plt.ylabel("PRA Total")
    plt.title("PRA Total for " + name)
    plt.grid(axis='y')
    plt.xlim([0, 4])
    plt.ylim([0, max(running_total)])
    plt.show()


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