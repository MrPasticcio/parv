import random

import numpy as np


class Player:
    def __init__(self):
        self.player_color = None

    def assign_color(self, player_color):
        self.player_color = player_color

    def move(self, configuration, valid_moves):
        pass

    def notify_results(self, result, final_configuration):
        pass


class RandomOpponent(Player):
    def move(self, configuration, valid_moves):
        return random.sample(valid_moves, 1)[0]


class VerticalPlayer(Player):
    def __init__(self):
        super().__init__()
        self.bet = np.random.randint(0, 7)

    def move(self, configuration, valid_moves):
        if self.bet not in valid_moves:
            self.bet = random.sample(valid_moves, 1)[0]

        return self.bet


class AnnoyingPlayer(Player):

    def move(self, configuration, valid_moves):
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

    def move(self, configuration, valid_moves):
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
