import time
import AI
import internal_game as game
import utility_functions
import display_node



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


