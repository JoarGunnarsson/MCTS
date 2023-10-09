import random
from AI import MCTS, LowestCard, Random, Node
import skitgubbe as gui
import time
import utility_functions as utils


class Board:
    """Class representing the game state."""

    def __init__(self):
        """Initializing the game. Creates players and state variables."""
        self.turn = 1
        self.starting_cards = 3
        player1_id = random.randint(50, 100)
        player2_id = player1_id - 5
        self.player1 = Player(None, "Human Guy")
        self.player1.id = player1_id
        self.player2 = Player(MCTS(allowed_time=3, number_of_trees=30), "MCTS Man")
        self.player2.id = player2_id
        players = [self.player1, self.player2]
        random_index = random.randint(0, 1)
        self.turn_player = players[random_index]
        self.non_turn_player = players[random_index - 1]
        self.winner = None

        self.deck = new_deck()

        random.shuffle(self.deck)
        self.removed_cards = []

        self.player1.hand = self.deck[:self.starting_cards]
        del self.deck[:self.starting_cards]
        self.player2.hand = self.deck[:self.starting_cards]
        del self.deck[:self.starting_cards]

        self.pile = [Card("Pile of Bottom")]

    def end_turn(self):
        """Ends the current turn by switching who is the turn player."""
        self.turn_player, self.non_turn_player = self.non_turn_player, self.turn_player
        self.turn += 1

    def draw(self, player):
        if len(self.deck) != 0:
            player.hand.append(self.deck[0])
            del self.deck[0]

    def check_winning_position(self):
        """Checks if the current board is a win for either player. A player with 0 cards in their hand has won.
        If the turn count exceeds 300, the MCTS player (or player 2 in general) loses."""
        if (len(self.player1.hand) == 0 and len(self.deck) == 0) or self.turn >= 300:
            self.winner = self.player1
            return True
        elif len(self.player2.hand) == 0 and len(self.deck) == 0:
            self.winner = self.player2
            return True
        return False

    def legal_moves(self):
        """Returns the legal moves for the turn player."""
        legal_moves = []
        if self.turn_player.can_pass:
            legal_moves.append("pass")
            for card in self.turn_player.hand:
                if card.value == self.pile[-1].value:
                    legal_moves.append(card)
            return legal_moves

        for card in self.turn_player.hand:
            is_special_card = card.value == 2 or card.value == 10
            if card.value >= self.pile[-1].value or is_special_card:
                legal_moves.append(card)

        if len(self.pile) > 1:
            legal_moves.append("pile")
        if len(self.deck) != 0:
            legal_moves.append("chance")

        return legal_moves

    def determinize(self):
        """Returns a determinized board state, where the cards and their order in the deck and in the opponents hand
        are randomized, and chosen from the currently unseen cards."""
        new_board = self.copy()
        cards_in_opponents_hand = len(new_board.non_turn_player.hand)
        new_board.non_turn_player.hand = []
        base_deck = new_deck()
        deck = []
        for card in base_deck:
            if card.name in utils.card_names(self.pile) or card.name in utils.card_names(self.removed_cards) or \
                    card.name in utils.card_names(self.turn_player.hand):
                continue
            if card.name in utils.card_names(self.turn_player.seen_cards):
                new_board.non_turn_player.hand.append(card)
                continue

            else:
                deck.append(card)

        random.shuffle(deck)
        new_board.deck = deck

        while len(new_board.non_turn_player.hand) != cards_in_opponents_hand:
            new_board.draw(new_board.non_turn_player)

        # TODO: FIX
        return new_board

    def play_move(self, move, real_game=True):
        """Makes the turn player play the given move. Takes the move as input."""
        if move == "chance":
            card = self.deck[0]
            self.pile.append(card)
            if real_game and card not in self.player1.seen_cards:
                self.player1.seen_cards.append(card)
            if real_game and card not in self.player2.seen_cards:
                self.player2.seen_cards.append(card)
            del self.deck[0]
            not_special_card = card.value != 2 and card.value != 10
            if card.value < self.pile[-2].value and not_special_card:
                self.turn_player.hand.extend(self.pile[1:])
                del self.pile[1:]
                self.turn_player.can_pass = True
                return

            top_four_card_values = card_values(self.pile[-4:])
            if card.value == 10 or top_four_card_values.count(card.value) == 4:
                self.removed_cards.extend(self.pile[1:])

                if real_game:
                    for card in self.pile[1:]:
                        safe_remove(self.player1.seen_cards, card)
                        safe_remove(self.player2.seen_cards, card)

                del self.pile[1:]
                self.turn_player.can_pass = False
                return

            self.turn_player.can_pass = True
            return

        elif move == "pass":
            self.turn_player.can_pass = False
            self.end_turn()
            return

        elif move == "pile":
            self.turn_player.hand.extend(self.pile[1:])
            del self.pile[1:]
            self.turn_player.can_pass = True
            return

        card = move
        self.pile.append(card)

        if real_game and card not in self.player1.seen_cards:
            self.player1.seen_cards.append(card)
        if real_game and card not in self.player2.seen_cards:
            self.player2.seen_cards.append(card)

        self.turn_player.hand.remove(card)

        if len(self.turn_player.hand) < 3:
            self.draw(self.turn_player)

        top_four_card_values = card_values(self.pile[-4:])
        if card.value == 10 or len(top_four_card_values) == 4 and top_four_card_values.count(
                top_four_card_values[0]) == 4:
            self.removed_cards.extend(self.pile[1:])
            if real_game:
                for card in self.pile[1:]:
                    safe_remove(self.player1.seen_cards, card)
                    safe_remove(self.player2.seen_cards, card)

            del self.pile[1:]
            self.turn_player.can_pass = False
            return
        self.turn_player.can_pass = True
        return

    def play_one_turn(self, real_game=False):
        self.turn_player.play(self, real_game)
        if self.check_winning_position():
            return False
        return True

    def play_one_game(self, real_game=False):
        # Game loop
        while True:
            continue_playing = self.play_one_turn(real_game)
            if not continue_playing:
                break
        return self

    def __repr__(self):
        return "\n" + "-" * 30 \
            + "\n" + "Turn: " + str(self.turn) + ". Cards left in deck: " + str(len(self.deck)) \
            + "\n" + self.turn_player.name + "'s hand: " + str(self.turn_player.hand) + "\n" \
            + self.non_turn_player.name + "'s hand: " + str(self.non_turn_player.hand) + "\n" \
            + str(self.pile[-5:]) + "\n" \
            + "-" * 30 + "\n" \
            + str(self.deck) + "\n" \
            + str(self.pile) + "\n" \
            + str(self.removed_cards) + "\n"

    def copy(self):
        new_board = Board()
        new_board.deck = copy_card_list(self.deck)

        new_board.player1 = self.player1.copy()
        new_board.player2 = self.player2.copy()
        if self.turn_player == self.player1:
            new_board.turn_player = new_board.player1
            new_board.non_turn_player = new_board.player2
        else:
            new_board.turn_player = new_board.player2
            new_board.non_turn_player = new_board.player1

        new_board.removed_cards = copy_card_list(self.removed_cards)

        new_board.pile = copy_card_list(self.pile)
        new_board.turn = self.turn
        new_board.winner = self.winner
        return new_board


class Player:
    """Class representing each player."""

    def __init__(self, ai, name="Player"):
        """Initializing the player. Takes the type of AI as input."""
        self.name = name
        self.hand = []
        self.ai = ai
        self.id = 0
        self.seen_cards = []
        self.can_pass = False

    def set_ai(self, ai):
        self.ai = ai

    def set_name(self, name):
        self.name = name

    def play(self, board, real_game=False):
        """Continues to roll the dice until either a one is rolled, or the AI decides to not roll again."""
        if real_game:
            # TODO: This should be left to the GUI.
            print("Computing the next move...")
        move = self.ai.compute_next_move(board)
        if real_game:
            gui.print_screen(board_string(board))
            print(gui.move_string(move, board))
            gui.continue_button()
            gui.print_screen(board_string(board))
        board.play_move(move, real_game=real_game)

    def copy(self):
        new_player = Player(self.ai, self.name)

        new_player.hand = copy_card_list(self.hand)

        new_player.id = self.id

        new_player.seen_cards = copy_card_list(self.seen_cards)
        return new_player

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.id == other.id


class Card:
    def __init__(self, name, value=None):
        self.name = name
        if value is None:
            self.value = utils.get_card_value(name)
        else:
            self.value = value

    def __repr__(self):
        return self.name


def new_deck():
    suits = ["Hearts", "Diamonds", "Spades", "Clubs"]
    values = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"]
    deck = [Card(value + " of " + suit) for suit in suits for value in values]
    return deck


def card_values(card_list):
    values = []
    for card in card_list:
        values.append(card.value)
    return values


def copy_card_list(card_list):
    new_card_list = []
    for card in card_list:
        new_card_list.append(card)
    return new_card_list


def safe_remove(card_list, card_to_remove):
    """Removes a given card from a list if the card is in the list, and does nothing otherwise. Removes all copies."""
    for card in card_list.copy():
        if card == card_to_remove:
            card_list.remove(card)


def board_string(game_board):
    """Returns a string showing the current board state, from the perspective of the human player. Assumes the human
    is player 1."""
    cards_in_pile = str(len(game_board.pile) - 1)
    if cards_in_pile == "1":
        pile_card_string = "card"
    else:
        pile_card_string = "cards"

    # TODO: This should be in the GUI file. Change "?" to _.name for debugging cards.
    return "\n" + "Turn: " + str(game_board.turn) + ". Cards left in the deck: " + str(len(game_board.deck)) \
        + "\n" + "Pile (" + str(cards_in_pile) + " " + pile_card_string + "): " + str(game_board.pile[1:][-1:-5:-1]) \
        + "..." * (len(game_board.pile) >= 5) \
        + "\n" + game_board.player2.name + "'s hand: " + str(["?" for _ in game_board.player2.hand]) \
        + "\n" + "Your hand: " + str(game_board.player1.hand) + "\n"


def test_determinize():
    board = Board()
    p1 = board.player1
    p2 = board.player2
    board.turn_player = p1
    board.non_turn_player = p2
    board_copy = board.copy()
    for card in board_copy.deck:
        if card.name in ["Test of Hearts", "Test of Clubs"]:
            board.deck.remove(card)

    for card in board_copy.player1.hand:
        if card.name in ["Test of Hearts", "Test of Clubs"]:
            p1.hand.remove(card)

    for card in board_copy.player2.hand:
        if card.name in ["Test of Hearts", "Test of Clubs"]:
            p2.hand.remove(card)

    while len(p1.hand) < 3:
        board.draw(p1)

    while len(p2.hand) < 3:
        board.draw(p2)

    print(board)
    p1.hand.append(Card("Test of Hearts", 15))
    p2.hand.append(Card("Test of Clubs", 15))
    board.play_move(p1.hand[-1])
    board.end_turn()
    board.play_move(p2.hand[-1])
    board.end_turn()
    board.play_move("pile")
    board.end_turn()
    det_board = board.determinize()
    human_hand = det_board.non_turn_player.hand

    test_of_hearts_in_hand = False
    test_of_clubs_in_hand = False
    for card in human_hand:
        if card.name == "Test of Hearts":
            test_of_hearts_in_hand = True
        if card.name == "Test of Clubs":
            test_of_clubs_in_hand = True

    print(det_board)
    print(board)
    assert test_of_clubs_in_hand
    assert test_of_hearts_in_hand

    board = Board()
    p1 = board.player1
    p2 = board.player2
    board.turn_player = p1
    board.non_turn_player = p2
    board_copy = board.copy()
    for card in board_copy.deck:
        if card.name in ["Test of Hearts", "Test of Clubs", "Test of Tens"]:
            board.deck.remove(card)

    for card in board_copy.player1.hand:
        if card.name in ["Test of Hearts", "Test of Clubs", "Test of Tens"]:
            p1.hand.remove(card)

    for card in board_copy.player2.hand:
        if card.name in ["Test of Hearts", "Test of Clubs", "Test of Tens"]:
            p2.hand.remove(card)

    while len(p1.hand) < 3:
        board.draw(p1)

    while len(p2.hand) < 3:
        board.draw(p2)

    p1.hand.append(Card("Test of Tens", 10))
    p1.hand.append(Card("Test of Hearts", 15))
    p2.hand.append(Card("Test of Clubs", 15))
    board.play_move(p1.hand[-1])
    board.end_turn()
    board.play_move(p2.hand[-1])
    board.end_turn()
    board.play_move(p1.hand[-1])
    board.play_move("chance")
    board.end_turn()
    det_board = board.determinize()
    human_hand = det_board.non_turn_player.hand
    deck = det_board.deck

    for card in human_hand:
        assert card.name not in ["Test of Tens", "Test of Hearts", "test of Clubs"]

    for card in deck:
        assert card.name not in ["Test of Tens", "Test of Hearts", "test of Clubs"]


def test_simulation_runtime():
    iterations = 50000
    total_time = 0
    for i in range(iterations):
        board = Board()
        board_node = Node(parent=None, board=board)
        start_time = time.time()
        board.player2.ai.simulation(board_node)
        stop_time = time.time()
        total_time += stop_time - start_time

    print(total_time, total_time / iterations)


def test_mcts_vs_lowest():
    number_of_games = 100
    mcts_score = 0
    lowest_score = 0
    for game_number in range(number_of_games):
        game_board = Board()
        game_board.player1.set_ai(LowestCard())
        game_board.player1.set_name("LowestCard Guy")
        game_board.play_one_game()
        if game_board.winner.name == "LowestCard Guy":
            lowest_score += 1
        else:
            mcts_score += 1

        print("Winner of game", game_number, "was", game_board.winner)
        print("Current score:")
        print("MCTS:", mcts_score)
        print("LowestCard:", lowest_score)
        print(game_board)
        print("\n" * 5)


def test_mcts_vs_mcts():
    number_of_games = 100
    p1_score = 0
    p2_score = 0
    for game_number in range(number_of_games):
        game_board = Board()
        game_board.player1.set_ai(MCTS(allowed_time=1))
        game_board.player1.set_name("Player1")
        game_board.player2.set_ai(MCTS(allowed_time=1, number_of_trees=10))
        game_board.player2.set_name("Player2")
        game_board.play_one_game()
        if game_board.winner.name == "Player1":
            p1_score += 1
        else:
            p2_score += 1

        print("Winner of game", game_number, "was", game_board.winner)
        print("Current score:")
        print("Player1:", p1_score)
        print("Player2:", p2_score)
        print(game_board)
        print("\n" * 5)
