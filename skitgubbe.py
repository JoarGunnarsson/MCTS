import os
import tty
import sys
import internal_game as game
import AI
import time

sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=32, cols=170))
os.system('clear')

tty.setcbreak(sys.stdin)


# TODO: Om ai:n lägger 4 och vänder, visa det tydligare. T.ex the AI plays the 4 of Clubs and clears the pile.
# TODO: Förbättra LowestCard(), så att mcts blir snabbare och bättre.
# TODO: Hur många träd är bäst? Hur mycket tid ska ai:n få? Är 1.41 det bästa värdet på c? Ska man utforska mer/mindre?
# TODO: Implement best-child property for a node?
# TODO: Add a menu for selecting the difficulty (the time the AI has to play).
# TODO: Implement some more tests? For example, does determinize work?
# TODO: After 'The AI plays...', update the board_string before computing the next move.
# TODO: Perhaps create a move for playing 2 of the same cards, so the user doesnt have to wait for so long.
# TODO: Why does the MCTS ai always try to pick up the pile or chance? If playing 4 of a kind is not possible,
# the ai loses every game (for example by removing some cards from the deck). This should not happen.
# TODO: In the gui, perhaps show every card, but pressing enter on cards that are too low does nothing?

class Button:
    def __init__(self, name, key="", can_be_pressed=True):
        self.name = name
        self.key = key
        self.can_be_pressed = can_be_pressed


def print_screen(string):
    """Clears window and prints the provided string."""
    os.system('clear')
    print(string)


def key_press():
    """Uses stdin to get a keypress. Returns what that keypress means. Pauses until key is pressed. Does not
    support arrow keys, they are treated as the escape button."""
    key = ord(sys.stdin.read(1))
    if key == 97:
        # a
        return "left"

    elif key == 100:
        # d
        return "right"

    elif key == 115:
        # s
        return "down"

    elif key == 119:
        # w
        return "up"

    elif key == 10:
        # Enter
        return "enter"

    elif key == 27:
        # Escape
        return "quit"


def continue_button():
    """Creates a '|Continue|' button. Freezes screen until 'Enter' is pressed."""
    print("\n" + "|Continue|")
    while True:
        key = ord(sys.stdin.read(1))
        if key == 10:
            break
        elif key == 224:
            sys.stdin.read(1)
        elif key == 13:
            sys.exit()


def button_menu(string, buttons):
    """Creates a menu for any number of buttons and a label. Returns a string representing the selected button."""
    display_buttons = [["|" + btn.name + "|" for btn in row] for row in buttons]
    y = 0
    rows_to_display = 3
    visible_buttons_per_row = 5
    x_positions = [0 for _ in range(len(buttons))]
    x_shifts = [0 for _ in range(len(buttons))]
    while True:
        selected_x = min(x_positions[y], len(buttons[y]))
        menu_string = "\t" + string + "\n\n"
        for i in range(0, min(rows_to_display, len(buttons))):
            menu_string += "\t"
            if x_shifts[i] > 0:
                menu_string += "..."
            menu_string += (" " * 10).join(display_buttons[i][x_shifts[i]:x_shifts[i] + visible_buttons_per_row])
            if x_shifts[i] + visible_buttons_per_row < len(buttons[i]):
                menu_string += "..."
            menu_string += "\n"

            if i == y:
                ellipsis_at_the_start = 3 * (x_shifts[i] > 0)
                letters_in_previous_buttons = len("".join(display_buttons[y][x_shifts[y]:selected_x]))
                spaces_for_previous_buttons = 10 * len(display_buttons[y][x_shifts[y]:selected_x])
                letters_in_the_selected_button = len(display_buttons[y][selected_x])
                number_of_spaces = ellipsis_at_the_start + letters_in_previous_buttons + spaces_for_previous_buttons
                menu_string += "\t" + " " * number_of_spaces + "-" * letters_in_the_selected_button
            menu_string += "\n"
        print_screen(menu_string)
        command = key_press()
        if command == "left":
            x_positions[y] -= 1
        elif command == "right":
            x_positions[y] += 1
        elif command == "up":
            y -= 1
        elif command == "down":
            y += 1
        elif command == "enter" and buttons[y][x_positions[y]].can_be_pressed:
            return buttons[y][x_positions[y]]
        elif command == "quit":
            return Button(name="exit", key="exit")

        y = clamp(y, 0, len(buttons) - 1)
        x_positions[y] = clamp(x_positions[y], 0, len(buttons[y]) - 1)

        if x_positions[y] >= x_shifts[y] + visible_buttons_per_row:
            x_shifts[y] += 1
        elif x_shifts[y] > x_positions[y] >= 0:
            x_shifts[y] -= 1

        x_shifts[y] = clamp(x_shifts[y], 0, len(buttons[0]) - visible_buttons_per_row)


def clamp(x, lowerBound=0, upperBound=1):
    """Clamps a number between an upper and lower bound. Default bounds are [0,1]."""
    if lowerBound > upperBound:
        lowerBound, upperBound = upperBound, lowerBound
    return max(min(x, upperBound), lowerBound)


def move_string(move, game_board):
    if move == "pass":
        return "The AI ends their turn."
    elif move == "pile":
        return "The AI picks up all cards in the pile."
    elif move == "chance":
        return "The AI plays the top card of the deck, the " + game_board.deck[0].name + "."
    else:
        return "The AI plays the card " + move.name + "."


def game_loop(game_state, game_board):
    """Runs the game state the game is currently in. Takes the initial game state as input and returns the resulting
    game state and board state as output."""
    if game_state == "main_menu":
        return main_menu()

    elif game_state == "in_game":
        return in_game(game_board)

    elif game_state == "win_screen":
        print("Player " + game_board.winner.name + " has won the game.")
        continue_button()
        return "main_menu", None

    else:
        print("Undefined game state")
        return "main_menu", None


def main_menu():
    selected_button = button_menu("Main Menu", [
        [Button("Start Game", "start"), Button("Exit Game", "exit"), Button("Test", "test")]])
    if selected_button.key == "start":
        game_board = game.Board()
        return "in_game", game_board

    elif selected_button.key == "exit":
        return "exit", None

    elif selected_button.key == "test":
        test()
        return "exit", None


def in_game(game_board):
    while True:
        if game_board.turn_player.ai is None:
            play_human(game_board)
            if game_board.check_winning_position():
                return "win_screen", game_board

        elif game_board.turn_player.ai is not None:

            continue_playing = game_board.play_one_turn(real_game=True)
            if not continue_playing:
                return "win_screen", game_board


def play_human(game_board):
    while True:
        AI.card_sort(game_board.turn_player.hand)
        menu_string = game.board_string(game_board) + "Possible actions:"
        legal_moves = game_board.legal_moves()
        moves = legal_moves.copy()
        if "chance" in moves:
            moves.remove("chance")
        if "pile" in moves:
            moves.remove("pile")
        if "pass" in moves:
            moves.remove("pass")

        AI.card_sort(moves)
        cards = [Button(str(move), move) for move in moves]
        misc_moves = []
        if "pass" in legal_moves:
            misc_moves.append(Button("End your turn", "pass"))
        if "chance" in legal_moves:
            misc_moves.append(Button("Chance", "chance"))
        if "pile" in legal_moves:
            misc_moves.append(Button("Pick up the pile", "pile"))
        if len(game_board.pile) > 1:
            misc_moves.append(Button("Take a closer look at the pile", "look_pile"))
        if len(cards) == 0 and len(misc_moves) != 0:
            actions = [misc_moves]
        elif len(cards) != 0 and len(misc_moves) == 0:
            actions = [cards]
        else:
            actions = [cards, misc_moves]

        selected_button = button_menu(menu_string, actions)
        if selected_button.key == "look_pile":
            card_buttons = [Button(card.name, card, False) for card in game_board.pile[-1:0:-1]]
            button_menu("Pile: ", [card_buttons, [Button("Continue")]])
        else:
            if selected_button.key == "chance":
                print("The top card of the deck is " + game_board.deck[0].name + ".")
                continue_button()
            game_board.play_move(selected_button.key)

        break


def main():
    game_state = "main_menu"
    game_board = None
    while True:
        game_state, game_board = game_loop(game_state, game_board)
        if game_state == "exit":
            break


def test():
    print("Starting the test procedure.")
    test_chance_lower_card()
    test_chance_four_card_flip()
    test_mcts_runtime()
    # game.test_determinize()
    # game.test_simulation_runtime()
    test_mcts_node_count()
    print("Testing over.")
    collect_data()


def collect_data():
    # game.test_mcts_vs_lowest()
    game.test_mcts_vs_mcts()


def test_chance_lower_card():
    game_board = game.Board()
    game_board.turn_player = game_board.player1
    game_board.non_turn_player = game_board.player2
    game_board.player1.hand = []
    game_board.player2.hand = []
    game_board.pile.append(game.Card("Ace of Hearts"))
    game_board.deck[0] = game.Card("Four of Diamonds")
    game_board.play_move("chance")
    assert len(game_board.pile) == 1 and sorted(game.card_values(game_board.player1.hand)) == [4, 14]


def test_chance_four_card_flip():
    game_board = game.Board()
    game_board.turn_player = game_board.player1
    game_board.non_turn_player = game_board.player2
    game_board.player1.hand = []
    game_board.player2.hand = []

    game_board.player1.hand.append(game.Card("Ace of Spades"))
    game_board.pile.append(game.Card("Four of Hearts"))
    game_board.pile.append(game.Card("Four of Spades"))
    game_board.pile.append(game.Card("Four of Clubs"))
    game_board.deck[0] = game.Card("Four of Diamonds")
    game_board.play_move("chance")
    assert game_board.legal_moves() != ["pass"]


def test_mcts_runtime():
    game_board = game.Board()
    game_board.deck.extend(game_board.player1.hand)
    game_board.deck.extend(game_board.player2.hand)
    AI.card_sort(game_board.deck)
    game_board.pile.append(game_board.deck[-1])
    del game_board.deck[-1]

    game_board.turn_player = game_board.player2
    game_board.non_turn_player = game_board.player1
    game_board.player1.hand = []
    game_board.player2.hand = []
    for _ in range(3):
        game_board.draw(game_board.player1)

    for _ in range(3):
        game_board.draw(game_board.player2)

    move = game_board.player2.ai.compute_next_move(game_board)
    print(move_string(move, game_board))


def test_mcts_node_count():
    number_of_trials = 10
    total_root_visits = 0
    for i in range(number_of_trials):
        game_board = game.Board()
        game_board.player2.set_ai(AI.MCTS(allowed_time=1))
        game_board.turn_player = game_board.player2
        root_node = AI.Node(None, game_board)
        start_time = time.time()
        time_per_tree = game_board.turn_player.ai.allowed_time / game_board.turn_player.ai.number_of_trees
        while time.time() - start_time < max(time_per_tree, 0.05):
            game_board.turn_player.ai.mcts_round(root_node)
        total_root_visits += root_node.n

    print("Average root node visits:", total_root_visits / number_of_trials)


if __name__ == '__main__':
    main()
