"""
Tic Tac Toe Player
"""

import math
import copy

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


def player(board):
    """
    Returns player who has the next turn on a board.
    """ #with X starting
    XCounter = 0
    OCounter = 0
    for row in board:
        for element in row:
            if element == X:
                XCounter += 1
            elif element == O:
                OCounter += 1
    if XCounter > OCounter:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possibleActions = []
    for row in range(3):
        for column in range(3):
            if board[row][column] == EMPTY:
                action = (row, column)
                possibleActions.append(action)
    return possibleActions



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    copyBoard = copy.deepcopy(board)
    element = player(board)
    i = action[0]
    j = action[1]
    copyBoard[i][j] = element
    return copyBoard

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #check rows
    for row in board:
        if row.count(X)==3 or row.count(O)==3:
            return row[0]
    #check columns
    for column in range(3):
        if not board[0][column] == EMPTY and board[0][column] == board[1][column] == board[2][column]:
            return board[0][column]
    #check diagonal
    if not board[0][0] == EMPTY and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    #check inverse diagonal    
    if not board[0][2] == EMPTY and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if not winner(board) == EMPTY:
        return True
    for row in board:
        if EMPTY in row:
            return False
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)

    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    a = -999999
    b = 999999
    playerTurn = player(board)
    if playerTurn == X:
        bestAction = None
        bestVal = -99999
        for action in actions(board):
            val = MinVal(result(board, action), a, b)
            a = max(a, val)
            if val > bestVal:
                bestVal = val
                bestAction = action
        return bestAction
    else:
        bestAction = None
        bestVal = 99999
        for action in actions(board):
            val = MaxVal(result(board, action), a, b)
            b = min(val, b)
            if val < bestVal:
                bestVal = val
                bestAction = action
        return bestAction

def MaxVal(board, a, b):
    if terminal(board):
        return utility(board)
    v = -9999999
    for action in actions(board):
        v = max(v, MinVal(result(board, action), a, b))
        a = max(a, v)
        if a >= b:
            break
    return v
def MinVal(board, a, b):
    if terminal(board):
        return utility(board)
    v = 9999999
    for action in actions(board):
        v = min(v, MaxVal(result(board, action), a, b))
        b = min(b, v)
        if a >= b:
            break
    return v