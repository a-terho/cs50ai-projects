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
    min_max = "max" if player(board) == X else "min"

    # Loop through all the possible actions this board can have. While doing
    #  that, calculate either the max or min value for each of these actions.
    action_values = []
    best_so_far = None
    for action in actions(board):

        # This part of the function could be implemented also by recursively
        #  calling the minimax(result(board, action)) directly !! You would
        #  need to find a way to implement alpha-beta pruning to it though...

        # We will assume the opponent wants to play optimally
        # For max player, opponent wants the lowest value possible
        if min_max == "max":
            value = min_value(result(board, action), best_so_far, prune="lower")

            # For max player, keep track of the highest low value so far
            if best_so_far is not None and value > best_so_far:
                best_so_far = value

        # For min player, opponent wants the highest value possible
        elif min_max == "min":
            value = max_value(result(board, action), best_so_far, prune="higher")

            # For min player, keep track of the lowest high value so far
            if best_so_far is not None and value < best_so_far:
                best_so_far = value

        # This is for alfa-beta pruning (best_so_far = alfa), initialization
        if best_so_far is None:
            best_so_far = value

        action_values.append((value, action))

    # Finally, out of all actions, choose only the best one for current player
    # action_values is a list of tuples with action value at [0] and action at [1]
    if min_max == "max":
        return max(action_values, key=lambda cell: cell[0])[1]

    elif min_max == "min":
        return min(action_values, key=lambda cell: cell[0])[1]


def max_value(board, best_so_far, prune):
    # If this board has no more actions, return its value
    if terminal(board):
        return utility(board)

    # The currently highest value is infinitely small
    value = -math.inf

    # For all allowed actions on this board...
    for action in actions(board):

        # Select the biggest of current max and following min
        value = max(value, min_value(result(board, action), best_so_far, prune))

        # If this value is higher than the current highest, there is
        #  a new higher high in this board. If pruning is active, we
        #  can stop looking further because this board will not be
        #  chosen when we are trying to look for the lowest value.
        if best_so_far is not None and value > best_so_far and prune == "higher":
            break

    return value


def min_value(board, best_so_far, prune):
    # If this board has no more actions, return its value
    if terminal(board):
        return utility(board)

    # The currently smallest value is infinitely big
    value = math.inf

    # For all allowed actions on this board...
    for action in actions(board):

        # Select the smallest of current min and following max
        value = min(value, max_value(result(board, action), best_so_far, prune))

        # If this value is lower than the current lowest, there is
        #  a new lower low in this board. If pruning is active, we
        #  can stop looking further because this board will not be
        #  chosen when we are trying to look for the highest value.
        if best_so_far is not None and value < best_so_far and prune == "lower":
            break

    return value
