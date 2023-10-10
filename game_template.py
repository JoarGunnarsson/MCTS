class Game:
    def __init__(self):
        self.winner = None
        self.turn_player = None
        pass

    def legal_moves(self):
        """Returns a list containing all legal moves"""
        pass

    def play_one_game(self):
        """Plays one complete game, starting from the current state"""
        return self

    def play_move(self, move):
        """Takes a move as input, and plays it."""

    def determinize(self):
        """Returns a determinized board. If the game has no hidden information/randomness, simply return self here."""
        pass

    def check_winning_position(self):
        """Should check if the current game state is a winning state, and return True/False."""
        pass

    def set_all_ai(self, new_ai):
        """Should set the AI for all players to 'new_ai()'."""
        pass

    def copy(self):
        """Should return a copy of self."""
        pass


class Player:
    def __init__(self):
        self.id = None
    pass

