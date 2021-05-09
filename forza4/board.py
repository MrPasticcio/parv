import logging
from copy import deepcopy

import numpy as np

from player import AnnoyingPlayer, AnnoyingPlayerV2, VerticalPlayer, RandomOpponent


class Board:
    def __init__(self):
        self._board = np.zeros((6, 7)).astype(int)

    @property
    def board(self):
        return deepcopy(self._board)

    def insert(self, position: int, player: int):
        assert player in [-1, 1], 'The player is either 1 or -1'
        assert self.is_valid_move(position), 'The provided position is not valid'

        x = int(position)
        y = 5 - np.abs(self._board[:, x]).sum()

        self._board[y, x] = player

        return self._board

    def is_valid_move(self, position):
        x = int(position)
        try:
            assert 0 <= position <= 6, 'The position must be between 0 and 6'
            y = 5 - np.abs(self._board[:, x]).sum()
            assert 0 <= y <= 5, 'The column is full'
            valid_move = True
        except AssertionError as e:
            logging.info(e)
            valid_move = False

        return valid_move

    @property
    def valid_moves(self):
        return np.where((6 - np.abs(self._board).sum(0)) > 0)[0].tolist()

    @staticmethod
    def is_winning_configuration(configuration):
        def check_sequence(sequence):
            nonlocal winning_config, winner

            conv = np.convolve(sequence, [1, 1, 1, 1], 'valid')
            if 4 in np.abs(conv):
                winning_config = True
                winner = int(conv[np.argmax(np.abs(conv))] / 4)

        winner = None
        winning_config = False

        for k in range(-2, 3):
            diag_left = configuration[np.eye(6, 7, k, dtype=bool)]
            check_sequence(diag_left)
            diag_right = configuration[np.flip(np.eye(6, 7, k, dtype=bool), axis=1)]
            check_sequence(diag_right)

        for row in configuration:
            check_sequence(row)

        for col in configuration.T:
            check_sequence(col)

        return winning_config, winner

    def __str__(self):
        cells_mapping = {1: 'o', 0: ' ', -1: 'x'}
        printed_board = ''
        for r in self._board:
            row = ' | '.join(map(cells_mapping.get, r))
            printed_board += f'| {row} |\n'

        return printed_board


class Game:
    game_over = False
    winner = 0
    turn = 0

    def __init__(self, starting_player: int = None):
        if starting_player is None:
            self.starting_player = int(np.round(np.random.random())) * 2 - 1
        assert self.starting_player in [-1, 1]

        self.current_player = self.starting_player
        self.configurations_so_far = [np.zeros((6, 7), dtype=int)]
        self.actions = []
        self._board = Board()

    @property
    def board(self):
        return deepcopy(self._board)

    def reset(self):
        self._board = Board()
        self.configurations_so_far = [np.zeros((6, 7), dtype=int)]
        self.actions = []
        self.game_over = False
        self.winner = 0
        self.turn = 0

    def insert(self, position: int):
        if not self.game_over:
            try:
                self.actions.append(position)
                self._board.insert(position, self.current_player)
                self.configurations_so_far.append(self._board.board)

                self.turn += 1
                self.current_player *= -1

                self.game_over, self.winner = Board.is_winning_configuration(self.board.board)
                if not self.game_over:
                    if np.abs(self._board.board).sum() == 42:
                        self.game_over, self.winner = True, 0
            except AssertionError as e:
                logging.warning(e)
                self.game_over = True
                self.winner = self.current_player * -1
        else:
            logging.warning('The game is over')

        return self.board, self.game_over

    @property
    def latest_configuration(self):
        return self.configurations_so_far[-1]


if __name__ == '__main__':
    game = Game()

    players_pool = [
        RandomOpponent(),
        AnnoyingPlayer(),
        AnnoyingPlayerV2(),
        VerticalPlayer(),
    ]

    winners = []
    players = []

    for g in range(10000):
        p1, p2 = np.random.choice(len(players_pool), 2, replace=False)
        current_players = {
            -1: players_pool[p1],
            1: players_pool[p2],
        }

        current_players[-1].assign_color(-1)
        current_players[1].assign_color(1)

        while not game.game_over:
            current_player = current_players[game.current_player]
            players_move = current_player.move(
                game.latest_configuration,
                game.board.valid_moves,
                game.current_player)
            game.insert(players_move)

        if game.winner == 0:
            for p in current_players.values():
                p.notify_results('draw', game.latest_configuration)
        else:
            current_players[game.winner].notify_results('won', game.latest_configuration)
            current_players[-1 * game.winner].notify_results('lost', game.latest_configuration)

        print(game.board)
        players.extend([p1, p2])

        if game.winner != 0:
            winners.append(p1 if game.winner == -1 else p2)
            print(f'P{p1} vs P{p2}: P{winners[-1]} won!')
        else:
            winners.append(None)
            print(f'P{p1} vs P{p2}: draw!')

        print(game.actions)

        for i, p in enumerate(players_pool):
            played = players.count(i)
            won = winners.count(i)

            recent_played = players[-500:].count(i)
            recent_won = winners[-250:].count(i)

            wr = won / played if played > 0 else 0
            recent_wr = recent_won / recent_played if recent_played > 0 else 0

            print(f'{p.name if hasattr(p, "name") else i}\tplayed:\t{played}'
                  f'\t\twin rate:\t{wr:.2%}\t\trecent win rate:\t{recent_wr:.2%}')

        game.reset()
