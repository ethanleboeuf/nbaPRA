import nba_funcs as nba
import pandas as pd


def main():
    overall_team_json = pd.read_json("http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams")
    data = overall_team_json._series
    teams = data["sports"][0]["leagues"][0]["teams"]
    teamColors = nba.get_team_colors(teams)

    player_dict = nba.get_player_dict("top300.csv")
    [player_dict, team_names] = nba.fill_player_dict(401161537, player_dict)

    nba.plot_player(player_dict, "Giannis Antetokounmpo", 30, teamColors, "Bucks")

    filename = team_names[0] + "vs" + team_names[1] + ".csv"
    nba.write_player_dict_to_csv(player_dict, "./data", filename)


if __name__ == "__main__":
    main()


print("ello world")