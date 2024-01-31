import math
import AI
import internal_game as game
import display_node


class Board:
    def __init__(self):
        self.player1 = game.Player(None, name="p1")
        self.player2 = game.Player(None, name="p2")
        self.player1.id = 1
        self.player2.id = -1
        self.turn_player = self.player1
        self.non_turn_player = self.player2

    def determinize(self):
        return self

    def legal_moves(self):
        return []

    def copy(self):
        new_board = Board()
        new_board.player1 = self.player1
        new_board.player2 = self.player2
        new_board.turn_player = self.turn_player
        new_board.non_turn_player = self.non_turn_player
        return new_board


def ucb1(node):
    wins = node.wins
    n = node.n
    if node.parent is None:
        print(10**10)
        return
    parentN = node.parent.n
    c = math.sqrt(2)
    print(wins / n + c * math.sqrt(math.log(parentN) / n))


def random_vs_lowestcard_simulationmethod():
    board = game.Board()
    board.player1.set_ai(AI.LowestCard())
    board.player2.ai.simulation_ai_type = AI.Random
    board.player2.ai.allowed_iterations=8000
    board.turn_player = board.player2
    board.non_turn_player = board.player1
    print(board)
    determinized_board = board.determinize()
    print(determinized_board)
    board.turn_player.ai.compute_next_move(board, determinized_board=determinized_board, fixed_det=True)
    board.turn_player.ai.simulation_ai_type = AI.LowestCard
    board.turn_player.ai.compute_next_move(board, determinized_board=determinized_board, fixed_det=True)


def test_mcts_round():
    root_board = Board()
    p1 = root_board.player1
    p2 = root_board.player2
    root_board.turn_player, root_board.non_turn_player = p1, p2
    root = AI.Node(None, root_board)
    root.n = 21
    root.wins = 11
    root.legal_moves = []

    level_2_base = root_board.copy()
    level_2_base.turn_player, level_2_base.non_turn_player = level_2_base.non_turn_player, level_2_base.turn_player
    lv2_1 = AI.Node(root, level_2_base.copy())
    lv2_1.n = 10
    lv2_1.wins = 7
    lv2_1.legal_moves = []
    lv2_2 = AI.Node(root, level_2_base.copy())
    lv2_2.n = 3
    lv2_2.wins = 0
    lv2_2.legal_moves = []
    lv2_3 = AI.Node(root, level_2_base.copy())
    lv2_3.n = 8
    lv2_3.wins = 3
    lv2_3.legal_moves = []
    root.children = [lv2_1, lv2_2, lv2_3]

    level_3_base = level_2_base.copy()
    level_3_base.turn_player, level_3_base.non_turn_player = level_3_base.non_turn_player, level_3_base.turn_player
    lv3_1 = AI.Node(lv2_1, level_3_base.copy())
    lv3_1.n = 4
    lv3_1.wins = 0
    lv3_1.legal_moves = []
    lv3_2 = AI.Node(lv2_1, level_3_base.copy())
    lv3_2.n = 6
    lv3_2.wins = 2
    lv3_2.legal_moves = []
    lv2_1.children = [lv3_1, lv3_2]

    lv3_3 = AI.Node(lv2_3, level_3_base.copy())
    lv3_3.n = 2
    lv3_3.wins = 1
    lv3_3.legal_moves = []
    lv3_4 = AI.Node(lv2_3, level_3_base.copy())
    lv3_4.n = 3
    lv3_4.wins = 2
    lv3_4.legal_moves = []
    lv3_5 = AI.Node(lv2_3, level_3_base.copy())
    lv3_5.n = 3
    lv3_5.wins = 2
    lv3_5.legal_moves = []
    lv2_3.children = [lv3_3, lv3_4, lv3_5]

    level_4_base = level_3_base.copy()
    level_4_base.turn_player, level_4_base.non_turn_player = level_4_base.non_turn_player, level_4_base.turn_player

    lv4_1 = AI.Node(lv3_2, level_4_base.copy())
    lv4_1.n = 3
    lv4_1.wins = 2
    lv4_1.legal_moves = []
    lv4_2 = AI.Node(lv3_2, level_4_base.copy())
    lv4_2.n = 3
    lv4_2.wins = 3
    lv4_2.legal_moves = []
    lv3_2.children = [lv4_1, lv4_2]

    ai = AI.MCTS()
    selected_node = ai.selection(root)

    display_node.show_tree(root)

    nodes = [root, lv2_1, lv2_2, lv2_3, lv3_1, lv3_2, lv3_3, lv3_4, lv3_5, lv4_1, lv4_2]

    print(selected_node.wins, selected_node.n)
    win = False
    ai.backpropagation(selected_node, win)
    display_node.show_tree(root)

test_mcts_round()




