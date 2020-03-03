import trends


def main():
    n = 3
    name = "Dejounte Murray"
    pra, targets, n = trends.get_last_n_games(n, name)
    trends.player_bar_graph(n, pra, targets, name)


if __name__ == "__main__":
    main()