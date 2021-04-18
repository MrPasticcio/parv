import numpy as np


class Player:
    def __init__(self):
        self.player_color = None

    def assign_color(self, player_color):
        self.player_color = player_color

    def move(self, configuration, check_valid_move):
        pass

    def notify_results(self, result):
        pass


class RandomOpponent(Player):
    def move(self, configuration, check_valid_move):
        is_valid = False
        my_move = 3
        while not is_valid:
            my_move = np.random.randint(0, 7)
            is_valid = check_valid_move(my_move)
        return my_move


class VerticalPlayer(Player):
    bet = np.random.randint(0, 7)

    def move(self, configuration, check_valid_move):
        is_valid = False
        my_move = None
        while not is_valid:
            my_move = self.bet
            is_valid = check_valid_move(my_move)
            if not is_valid:
                self.bet = np.random.randint(0, 7)

        return my_move


class AnnoyingPlayer(Player):

    def move(self, configuration, check_valid_move):
        occupied = np.abs(configuration).sum(0)
        order = sorted(range(7), key=lambda x: occupied[x], reverse=True)
        sorted_occupied = sorted(occupied, reverse=True)

        i = 0
        my_move = order[i]

        while sorted_occupied[i] >= 6:
            i += 1
            my_move = order[i]

        return my_move


class AnnoyingPlayerV2(Player):

    def move(self, configuration, check_valid_move):
        conf = -1 * configuration
        occupied = np.abs(conf).sum(0)
        opponent_occupation = -1 * np.clip(conf, -1, 0).sum(0)

        order = sorted(range(7), key=lambda x: opponent_occupation[x], reverse=True)
        sorted_occupied = [occupied[i] for i in order]

        i = 0
        my_move = order[i]

        while sorted_occupied[i] >= 6:
            i += 1
            my_move = order[i]

        return my_move