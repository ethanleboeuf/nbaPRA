import trends


def main():
    n = 9
    name = "Aaron Gordon"
    pra, targets, n = trends.get_last_n_games(n, name)
    trends.player_bar_graph(n, pra, targets, name)


if __name__ == "__main__":
    main()