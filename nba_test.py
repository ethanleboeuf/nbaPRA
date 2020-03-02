import nba_funcs as nba
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


def main():
    overall_team_json = pd.read_json("http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams")
    data = overall_team_json._series
    teams = data["sports"][0]["leagues"][0]["teams"]
    teamcolors = nba.get_team_colors(teams)
    player_dict = nba.get_player_dict("top300.csv")

    gid = 401161537

    [player_dict, team_names] = nba.fill_player_dict(gid, player_dict)
    image = plt.imread("player_images/giannis2.png")
    image = OffsetImage(image, zoom=0.35)

    flag = 0  # 0 means animation ONLY, change to 1 if you want a still image
    target_num = 30
    nba.plot_player_both(player_dict, "Giannis Antetokounmpo", target_num, teamcolors["Bucks"], image, flag)

    filename = str(gid) + "_" + team_names[0] + "vs" + team_names[1] + ".csv"
    nba.write_player_dict_to_csv(player_dict, "./data", filename)


if __name__ == "__main__":
    main()
