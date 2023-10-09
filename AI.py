import random
import math
import time
import numpy as np
import matplotlib.pyplot as plt


# Implement some way to fix the inherent randomness. Multiple trees might fix this.
# In non-deterministic games, with multiple nodes per turn, playing until you hit the opponents node could
# drastically shorten thinking time.
# TODO: Define API, what functions are needed for the AI to work.
# TODO: Are ties supported? Also, are multiple players supported? Nope.


class Node:
    """Class representing the nodes used for MCTS."""

    def __init__(self, parent, board):
        self.c = math.sqrt(2)
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

        new_child = Node(self, self.board.copy())
        new_child.board.play_move(move, real_game=False)
        new_child.move = move
        self.children.append(new_child)

        return new_child

    def show_tree(self):
        self.draw_tree(mode="all")
        plt.show()

    def draw_tree(self, left_edge=0, right_edge=500, depth=1, mode="all"):
        """Recursively draws the tree until depth TOTAL_DEPTH."""
        HEIGHT = 500
        TOTAL_DEPTH = 7
        if depth == TOTAL_DEPTH:
            return

        if mode == "all":
            nodes_to_visit = self.children
        else:
            if self.children is not None:
                nodes_to_visit = [mcts_select_node(self, mode="n")]
            else:
                nodes_to_visit = None
        self.x = int((right_edge - left_edge) / 2 + left_edge)
        self.y = int(HEIGHT - HEIGHT / TOTAL_DEPTH * depth)
        if self.board.turn_player.id == self.board.player1.id:
            color = "g"
        else:
            color = "r"

        if self.move == "chance" and self.parent is not None:
            move_str = "chance " + str(self.parent.board.deck[0])
        else:
            move_str = str(self.move)

        plt.text(self.x + 5, self.y + 5, move_str + ", " + str(self.board.turn_player))
        plt.text(self.x - 5, self.y - 5, str(self.wins) + "/" + str(self.n))
        if nodes_to_visit is None:
            plt.scatter(self.x, self.y, c=color, marker="s")
            return

        if depth == TOTAL_DEPTH - 1:
            plt.scatter(self.x, self.y, c=color, marker="v")
        else:
            plt.scatter(self.x, self.y, c=color)
        # Spaces the child nodes properly.
        length_per_child = (right_edge - left_edge) // len(nodes_to_visit)
        for i, child in enumerate(nodes_to_visit):
            self.children[i].draw_tree(left_edge + i * length_per_child, left_edge + (i + 1) * length_per_child,
                                       depth + 1, mode=mode)

        # Connects parents to their children with lines.
        if depth != TOTAL_DEPTH - 1:
            for i, child in enumerate(nodes_to_visit):
                plt.plot([self.x, self.children[i].x], [self.y, self.children[i].y], "k")

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
        moves = []
        special_cards = []
        for card in legal_moves:
            if type(card) == str:
                continue
            elif card.value == 2 and (board.pile[-1].value != 2 or board.pile[-1].last_played_by == board.turn_player.id) \
                    or card.value == 10:
                special_cards.append(card)
            else:
                moves.append(card)

        card_sort(moves)
        card_sort(special_cards)
        moves.extend(special_cards)
        if "pass" in legal_moves:
            moves.append("pass")
        elif "chance" in legal_moves:
            moves.append("chance")
        elif "pile" in legal_moves:
            moves.append("pile")
        return moves[0]

    def __repr__(self):
        return "LowestCard"


class MCTS(AI):
    """Class for the MCTS AI strategy."""

    def __init__(self, allowed_time=1, number_of_trees=1):
        AI.__init__(self)
        self.allowed_time = allowed_time
        self.number_of_trees = number_of_trees

    def compute_next_move(self, board):
        """Computes the next move, given the current state of the game. Returns True the number to be chosen."""

        time_per_tree = self.allowed_time / self.number_of_trees
        legal_moves = board.legal_moves()
        if len(legal_moves) == 1:
            return legal_moves[0]
        move_scores = [0 for _ in legal_moves]
        for tree in range(self.number_of_trees):
            determinized_board = board.determinize()
            root_node = Node(None, determinized_board)
            start_time = time.time()
            n = 0
            while time.time() - start_time < max(time_per_tree, 0.05):
                self.mcts_round(root_node)
                n += 1
            #root_node.show_tree()
            #print("Visits to the root node: " + str(root_node.n) + ". Allowed time: " + str(self.allowed_time) + " seconds.")
            best_child = mcts_select_node(root_node, "n")
            best_move = best_child.move
            for i, move in enumerate(legal_moves):
                if move == best_move:
                    move_scores[i] += best_child.n
                    break
        max_val = -1
        current_best = None
        for i, val in enumerate(move_scores):
            if val > max_val:
                max_val = val
                current_best = legal_moves[i]
        return current_best

    def mcts_round(self, root_node):
        # TODO: Rename this method.
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
        simulation_board.player1.ai = LowestCard()  # Hard coded, fix this? TODO
        simulation_board.player2.ai = LowestCard()  # Hard coded, fix this? TODO
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
        return "MCTS({})".format(self.allowed_time)


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
        return np.inf
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

