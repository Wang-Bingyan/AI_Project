# 游戏AI
import numpy as np
import random

# 评分表
value_table = [
    [[1, 1, 1, 1, 1], 50001],
    [[-1, -1, -1, -1, -1], -50000],

    [[0, 1, 1, 1, 1, 0], 4321],
    [[0, -1, -1, -1, -1, 0], -4320],

    [[0, 1, 1, 1, 0, 0], 721],
    [[0, -1, -1, -1, 0, 0], -720],

    [[0, 0, 1, 1, 1, 0], 721],
    [[0, 0, -1, -1, -1, 0], -720],

    [[0, 1, 1, 0, 1, 0], 721],
    [[0, -1, -1, 0, -1, 0], -720],

    [[0, 1, 0, 1, 1, 0], 721],
    [[0, -1, 0, -1, -1, 0], -720],

    [[1, 1, 1, 1, 0], 721],
    [[-1, -1, -1, -1, 0], -720],

    [[0, 1, 1, 1, 1], 721],
    [[0, -1, -1, -1, -1], -720],

    [[1, 1, 0, 1, 1], 721],
    [[-1, -1, 0, -1, -1], -720],

    [[1, 0, 1, 1, 1], 721],
    [[-1, 0, -1, -1, -1], -720],

    [[1, 1, 1, 0, 1], 721],
    [[-1, -1, -1, 0, -1], -720],

    [[0, 0, 1, 1, 0, 0], 121],
    [[0, 0, -1, -1, 0, 0], -120],

    [[0, 0, 1, 0, 1, 0], 121],
    [[0, 0, -1, 0, -1, 0], -120],

    [[0, 1, 0, 1, 0, 0], 121],
    [[0, -1, 0, -1, 0, 0], -120],

    [[0, 0, 0, 1, 0, 0], 21],
    [[0, 0, 0, -1, 0, 0], -20],

    [[0, 0, 1, 0, 0, 0], 21],
    [[0, 0, -1, 0, 0, 0], -20],
]


# AI接口，传入一张棋盘，返回下一步的行棋位置，row表示行，column表示列
def ai_move(board, neighborhood):
    size = np.size(board, 0)
    row = size // 2
    column = size // 2
    min_value = 114514

    # ================= 算法实现 =================
    for i in range(size):
        for j in range(size):
            if neighborhood[i][j] == 1 and board[i][j] == 0:
                if utility(board, i, j) < min_value:
                    row = i
                    column = j
                    min_value = utility(board, i, j)

    while board[row][column] != 0:
        row = random.randint(0, size - 1)
        column = random.randint(0, size - 1)
    # ===========================================

    return row, column


# 下在i行j列时的效用值
def utility(board, i, j):
    board[i][j] = -1
    board_T = np.transpose(board)
    board_m = np.flip(board, 0)
    value = 0

    # 行列扫描
    for x in range(np.size(board[0])):
        value += utility_line(board[x])
        value += utility_line(board_T[x])

    # 对角线扫描
    for x in range(-np.size(board) + 5, np.size(board) - 4):
        value += utility_line(board.diagonal(offset=x))
        value += utility_line(board_m.diagonal(offset=x))

    board[i][j] = 0
    return value


# 评估一条线上的棋形
def utility_line(line):
    for entry in value_table:
        if is_subsequence(line, entry[0]):
            return entry[1]
    return 0


# 判断b是否为a的子列表
def is_subsequence(a, b):
    for i in range(len(a) - len(b) + 1):
        flag = True
        for j in range(len(b)):
            if a[i + j] != b[j]:
                flag = False
                break
        if flag:
            return True
    return False
