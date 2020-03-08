import nba_funcs as nba
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


def main():
    overall_team_json = pd.read_json("http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams")
    data = overall_team_json._series
    teams = data["sports"][0]["leagues"][0]["teams"]
    teamcolors = nba.get_team_colors(teams)
    teamcolors["Jazz"] = "#002b5c"
    player_dict = nba.get_player_dict("top300.csv")

    gid = [401161561, 401161535, 401161519, 401161509, 401161494, 401161468, 401161450, 401161437, 401161419]
    player_name = "Aaron Gordon"
    flag = 2  # 0 means animation ONLY, change to 1 if you want a still image, 2 for just txt file
    target_num = [4.5, 4.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5]
    # line_color = teamcolors["Spurs"]
    line_color = "#069c47"
    for i, g in enumerate(gid):
        player_dict = nba.get_player_dict("top300.csv")
        [player_dict, team_names] = nba.fill_player_dict(g, player_dict)
        image = plt.imread("Player Pics/" + player_name + ".png")
        image = OffsetImage(image, zoom=0.35)
        nba.process_player(player_dict, player_name, target_num[i], line_color, image, flag, g)

        filename = str(gid[i]) + "_" + team_names[0] + "vs" + team_names[1] + ".csv"
        nba.write_player_dict_to_csv(player_dict, "./data", filename)


if __name__ == "__main__":
    main()
