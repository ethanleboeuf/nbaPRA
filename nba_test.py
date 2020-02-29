import nba_funcs as nba


def main():
    player_dict = nba.get_player_dict("top300.csv")
    player_dict = nba.fill_player_dict(401161528, player_dict)
    nba.plot_player(player_dict, "Kawhi Leonard", 30)


if __name__ == "__main__":
    main()


