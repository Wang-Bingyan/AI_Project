# 游戏AI
import numpy as np
import random


# AI接口，传入一张棋盘，返回下一步的行棋位置，row表示行，column表示列
def ai_move(board):
    size = np.size(board, 0)
    row = size // 2
    column = size // 2

    # ================= 算法实现 =================
    while board[row][column] != 0:
        row = random.randint(0, size - 1)
        column = random.randint(0, size - 1)

    # ===========================================

    return row, column
