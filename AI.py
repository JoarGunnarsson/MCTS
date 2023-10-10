import random
import math
import time
import utility_functions as utils

# Implement some way to fix the inherent randomness. Multiple trees might fix this.
# In non-deterministic games, with multiple nodes per turn, playing until you hit the opponents node could
# drastically shorten thinking time.
# TODO: Define API, what functions are needed for the AI to work.
# TODO: Are ties supported? Also, are multiple players supported? Nope.


class Node:
    """Class representing the nodes used for MCTS."""

    def __init__(self, parent, board, c=math.sqrt(2)):
        self.c = c
        self.children = None
        self.parent = parent
        self.wins = 0
        self.n = 0
        self.board = board
        self.move = None
        self.x = None
        self.y = None
        self.legal_moves = None

    def expand(self):
        """Creates the children of the current node, one for each possible action."""
        if self.legal_moves is None:
            self.children = []
            self.legal_moves = self.board.legal_moves()
        move = self.legal_moves.pop(0)

        new_child = Node(self, self.board.copy(), self.c)
        new_child.board.play_move(move, real_game=False)
        new_child.move = move
        self.children.append(new_child)

        return new_child

    def __repr__(self):
        return "Turn: " + str(self.board.turn) + ", Wins: " + str(self.wins) + ", Visits: " + str(self.n)


class AI:
    """Parent class for all AIs."""

    def __init__(self):
        pass


class Random(AI):
    """Class for the random AI strategy."""

    def __init__(self):
        AI.__init__(self)

    def compute_next_move(self, board):
        choices = board.legal_moves()
        return random.choice(choices)

    def __repr__(self):
        return "Random"


class LowestCard(AI):
    """Class for the AI strategy of continuing to roll until the target score is achieved, and then stopping."""

    def __init__(self):
        AI.__init__(self)

    def compute_next_move(self, board):
        """Computes the next move, given the current state of the game. Returns True if the chosen move is to roll
        again, and returns False otherwise."""
        legal_moves = board.legal_moves()
        current_min = 15
        saved_two = None
        saved_ten = None
        best_card = None
        saved_string_moves = []

        for card in legal_moves:
            if card in ["pass", "chance", "pile"]:
                saved_string_moves.append(card)
                continue

            elif card.value == 2:
                saved_two = card
                continue

            elif card.value == 10:
                saved_ten = card
                continue

            else:
                if card.value < current_min:
                    current_min = card.value
                    best_card = card

        if best_card is not None:
            return best_card

        if best_card is None and saved_two is not None:
            return saved_two

        if best_card is None and saved_ten is not None:
            return saved_ten

        if "pass" in saved_string_moves:
            return "pass"
        elif "chance" in saved_string_moves:
            return "chance"
        elif "pile" in saved_string_moves:
            return "pile"

        raise ValueError("No valid moves")

    def __repr__(self):
        return "LowestCard"


class MCTS(AI):
    """Class for the MCTS AI strategy."""

    def __init__(self, allowed_iterations=100, number_of_trees=1, c=math.sqrt(2), simulation_ai_type=LowestCard):
        AI.__init__(self)
        self.allowed_iterations = allowed_iterations
        self.number_of_trees = number_of_trees
        self.c = c
        self.simulation_ai_type = simulation_ai_type

    def compute_next_move(self, board, determinized_board=None, fixed_det=False):
        """Computes the next move, given the current state of the game. Returns True the number to be chosen."""
        iterations_per_tree = int(self.allowed_iterations / self.number_of_trees)
        legal_moves = board.legal_moves()
        if len(legal_moves) == 1:
            return legal_moves[0]
        move_scores = [0 for _ in legal_moves]
        for tree in range(self.number_of_trees):
            if determinized_board is None or fixed_det is False:
                determinized_board = board.determinize()
            root_node = Node(None, determinized_board, self.c)
            n = 0
            for iteration in range(iterations_per_tree):
                self.mcts_round(root_node)
                n += 1

            # display_node.show_tree(root_node)
            # print("Visits to the root node: " + str(root_node.n) + ". Allowed time: " + str(self.allowed_iterations) + " iterations.")
            best_child = mcts_select_node(root_node, "n")
            best_move = best_child.move
            for i, move in enumerate(legal_moves):
                if move == best_move:
                    move_scores[i] += 1  # TODO: Could this be better? best_child.n
                    break

        max_val = -1
        current_best = None
        for i, val in enumerate(move_scores):
            if val > max_val:
                max_val = val
                current_best = legal_moves[i]
        return current_best

    def mcts_round(self, root_node):
        node = self.selection(root_node)
        selected_node = self.expansion(node)
        if selected_node.board.winner is None:
            simulated_board = self.simulation(selected_node)
            selected_node_turn_player_win = selected_node.board.turn_player.id == simulated_board.winner.id

        else:
            selected_node_turn_player_win = selected_node.board.turn_player.id == selected_node.board.winner.id
        self.backpropagation(selected_node, selected_node_turn_player_win)

    def selection(self, node):
        """The selection step of the MCTS algorithm. Recursively selects nodes until a leaf node is reached."""
        if node.children is None or len(node.legal_moves) != 0:
            return node
        best_child = mcts_select_node(node, "score")
        return self.selection(best_child)

    def expansion(self, node):
        if node.board.check_winning_position():
            return node

        # Makes sure that each leaf node is simulated before having children.
        if node.children is None and node.n == 0:
            return node

        child_node = node.expand()

        child_node.board.check_winning_position()
        return child_node

    def simulation(self, node):
        simulation_board = node.board.copy()
        simulation_board.player1.ai = self.simulation_ai_type()  # TODO: Change this to board.set_all_ai(self.sim...)
        simulation_board.player2.ai = self.simulation_ai_type()
        board = simulation_board.play_one_game(real_game=False)
        return board

    def backpropagation(self, node, win):
        node.n += 1
        node.wins += int(win)
        if node.parent is None:
            return

        if node.board.turn_player.id != node.parent.board.turn_player.id:
            win = not win
        self.backpropagation(node.parent, win)

    def __repr__(self):
        return "MCTS({})".format(self.allowed_iterations)


def mcts_select_node(node, mode="score"):
    current_max_value = 0
    current_selected_node = None
    for child in node.children:
        value = mcts_score_node(child, node, mode)
        if value >= current_max_value:
            current_max_value = value
            current_selected_node = child
    return current_selected_node


def mcts_score_node(child, parent, mode="score"):
    if mode == "n":
        return child.n
    if child.n == 0:
        return 10**100
    if parent.board.turn_player.id == child.board.turn_player.id:
        return child.wins / child.n + child.c * math.sqrt(math.log(child.parent.n) / child.n)
    return (child.n - child.wins) / child.n + child.c * math.sqrt(math.log(child.parent.n) / child.n)


def card_sort(cards):
    """An in-place sorting algorithm that uses insertion sort to sort cards."""
    i = 1
    while i < len(cards):
        x = cards[i]
        j = i - 1
        while j >= 0 and cards[j].value > x.value:
            cards[j + 1] = cards[j]
            j = j - 1
        cards[j + 1] = x
        i = i + 1
