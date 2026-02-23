# fmt: off
"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]
# fmt: on


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    # As the only state variable we have available is the board, we need
    #  to check how many X's and O's it has to determine whose turn it is.
    Xs, Os = 0, 0
    for row in board:
        for cell in row:
            if cell == X:
                Xs += 1
            elif cell == O:
                Os += 1

    # If there are equal amount of Xs and Os, it's X's turn
    # Covers the initial state and every other state after that
    if Xs == Os:
        return X

    # Otherwise, it's O's turn
    return O

    # # If there are more Xs than Os, it's O's turn
    # if Xs > Os:
    #     return O

    # # Only case left if when there are more Os than Xs which shouln't be possible
    # raise Exception("Unexpected ending: more Os than Xs")


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    # Initialize the set for allowed actions
    allowed_actions = set()

    # Loop through the board to find EMPTY cells and
    #  add the indexes of those cells to the set
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                allowed_actions.add((i, j))

    return allowed_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # If specified action is not allowed, raise an exception
    if action not in actions(board):
        raise Exception("invalid action was given")

    # Create a deep copy of the current board
    new_board = [row[:] for row in board]

    # Insert the action to the new board
    player_symbol = player(board)
    new_board[action[0]][action[1]] = player_symbol

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Easiest way to implement this that I could think of is to
    #  loop the board once row-based, once column-based and once
    #  at each of the diagonals. If there are 3-in-row in any one
    #  of those, there is a winner that is indicated by the symbol.
    # The assumption is also that there can only be one winner.

    # We are assuming that the board is square
    row_count = len(board)
    column_count = len(board[0])

    # Row-based loop
    for i in range(row_count):
        first_symbol = board[i][0]
        if (
            all(first_symbol == board[i][j] for j in range(column_count))
            and first_symbol != EMPTY
        ):
            return first_symbol
    # for row in board:
    #     first_symbol = row[0]
    #     if all(first_symbol == symbol for symbol in row) and first_symbol != EMPTY:
    #         return first_symbol

    # Column-based loop
    for j in range(column_count):
        first_symbol = board[0][j]
        if (
            all(first_symbol == board[i][j] for i in range(row_count))
            and first_symbol != EMPTY
        ):
            return first_symbol

    # Diagonal based loops
    # First left-top to bottom-right
    first_symbol = board[0][0]
    if (
        all(first_symbol == board[i][i] for i in range(row_count))
        and first_symbol != EMPTY
    ):
        return first_symbol

    # Then left-bottom to top-right
    first_symbol = board[-1][0]
    if (
        all(first_symbol == board[-(1 + i)][i] for i in range(row_count))
        and first_symbol != EMPTY
    ):
        return first_symbol

    # If none of those return, there is no winner
    return None


# Terminal state check is done before selecting player
def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # Terminal state is reached when:
    # 1. There are no more possible moves left (board is full)
    # 2. There is a winner (three in a row)
    if not bool(actions(board)) or winner(board):
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    winner_symbol = winner(board)
    if winner_symbol == X:
        return 1
    elif winner_symbol == O:
        return -1

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # If board is a terminal board, return None (as per project declaration)
    if terminal(board):
        return None

    # First, get the current player and whether they are min (-1) or max (1)
    player_symbol = player(board)
    min_max = 1 if player_symbol == X else -1

    # Find the allowed actions for current board and calculate the value of
    #  each of the resulting boards. Bind actions with their values in the
    #  list of choices.
    allowed_actions = actions(board)
    choices = []
    for action in allowed_actions:
        board_value = calculate_value(result(board, action), min_max)

        # choices is list of tuples with board value at [0] and action at [1]
        choices.append((board_value, action))

    # print(f"Player {player_symbol} with min_max {min_max}")
    # print(choices)

    if min_max == 1:
        # Find the highest board value, and return corresponding action
        return max(choices, key=lambda cell: cell[0])[1]

    elif min_max == -1:
        # Find the lowest board value, and return corresponding action
        return min(choices, key=lambda cell: cell[0])[1]


def calculate_value(board, min_max):
    """
    Calculates the value of given board. It can be either -1, 0 or 1.

    Recursively checks the value of any non-terminal boards.
    """

    if not (min_max == 1 or min_max == -1):
        raise Exception("unexpected error")

    # Because this is a recursive function, first define the exit clause
    # Value of a terminal board is its value given by the utility function
    if terminal(board):
        return utility(board)

    # Find the allowed actions for the current board and
    #  construct the boards resulting from those actions
    allowed_actions = actions(board)
    board_values = []
    for action in allowed_actions:
        resulting_board = result(board, action)

        # For any non-terminal board, calculate the value of that board
        #  recursively while also shifting perspective at each recursion
        board_value = calculate_value(resulting_board, min_max * (-1))
        board_values.append(board_value)

    # If player is max, current board value is the highest value of its results
    if min_max == 1:
        return max(board_values)

    # Otherwise if player is min, current board value is the lowest of its results
    elif min_max == -1:
        return min(board_values)

    # # If resulting board is a terminal state, calculate its value with utility
    # if terminal(resulting_board):
    #     board_value = utility(resulting_board)
    # Otherwise, traverse further into the resulting boards, shifting perspective
