# 图形界面
import tkinter as tk
import tkinter.messagebox
import numpy as np
import sys
import game_ai

window = tk.Tk()
window.resizable(width=False, height=False)
window.title('五子棋')

line_width = 3  # 一根线的宽度
grid_width = 40  # 一个格子的宽度
border_width = 40  # 边界的宽度

size = 15 * line_width + 14 * grid_width + 2 * border_width  # 尺寸

game_board = np.zeros([15, 15])  # 棋盘用numpy数组表示
neighbourhood = np.zeros([15, 15])  # 邻域，用于缩小搜索范围

# 绘制棋盘
canvas = tk.Canvas(window, background='white', width=size, height=size)
img_board = tk.PhotoImage(file="images/board.png")
img_piece_black = tk.PhotoImage(file="images/piece_black.png")
img_piece_white = tk.PhotoImage(file="images/piece_white.png")
canvas.create_image(size // 2, size // 2, image=img_board)
canvas.pack()


# 绘制棋子
def draw_pieces(_canvas, row, column, player):
    pos_x = border_width + line_width // 2 + 1 + (grid_width + line_width) * column
    pos_y = border_width + line_width // 2 + 1 + (grid_width + line_width) * row
    if player == 1:  # 白棋
        _canvas.create_image(pos_x, pos_y, image=img_piece_black)
    elif player == -1:  # 黑棋
        _canvas.create_image(pos_x, pos_y, image=img_piece_white)


# 游戏胜负判定
def judge(board):
    board_t = board.transpose()
    board_mirror = np.flip(board, 0)
    # 行与列
    for i in range(15):
        for j in range(11):
            # 5个一行
            if (board[i][j: j + 5] == [1, 1, 1, 1, 1]).all():
                return 1
            elif (board[i][j: j + 5] == [-1, -1, -1, -1, -1]).all():
                return -1
            # 5个一列
            if (board_t[i][j: j + 5] == [1, 1, 1, 1, 1]).all():
                return 1
            elif (board_t[i][j: j + 5] == [-1, -1, -1, -1, -1]).all():
                return -1
    # 对角线
    for i in range(11):
        for j in range(11):
            if board[i][j] == 1 and board[i + 1][j + 1] == 1 and board[i + 2][j + 2] == 1 \
                    and board[i + 3][j + 3] == 1 and board[i + 4][j + 4] == 1:
                return 1
            elif board[i][j] == -1 and board[i + 1][j + 1] == -1 and board[i + 2][j + 2] == -1 \
                    and board[i + 3][j + 3] == -1 and board[i + 4][j + 4] == -1:
                return -1
            if board_mirror[i][j] == 1 and board_mirror[i + 1][j + 1] == 1 and board_mirror[i + 2][j + 2] == 1 \
                    and board_mirror[i + 3][j + 3] == 1 and board_mirror[i + 4][j + 4] == 1:
                return 1
            elif board_mirror[i][j] == -1 and board_mirror[i + 1][j + 1] == -1 and board_mirror[i + 2][j + 2] == -1 \
                    and board_mirror[i + 3][j + 3] == -1 and board_mirror[i + 4][j + 4] == -1:
                return -1
    return 0

def f(n):
    if n < 0:
        return 0
    if n > size:
        return size
    else:
        return n


# 鼠标事件
def onclick(event):
    column = (event.x - border_width // 2) // (line_width + grid_width)
    row = (event.y - border_width // 2) // (line_width + grid_width)

    if 0 <= column <= 14 and 0 <= row <= 14:
        if game_board[row][column] == 0:
            game_board[row][column] = 1  # 玩家行棋

            # 更新邻域
            try:
                neighbourhood[f(row - 1)][f(column - 1)] = \
                    neighbourhood[f(row)][f(column - 1)] = \
                    neighbourhood[f(row + 1)][f(column - 1)] = \
                    neighbourhood[f(row - 1)][f(column)] = \
                    neighbourhood[f(row + 1)][f(column)] = \
                    neighbourhood[f(row - 1)][f(column + 1)] = \
                    neighbourhood[f(row)][f(column + 1)] = \
                    neighbourhood[f(row + 1)][f(column + 1)] = 1
            except:
                pass

            draw_pieces(canvas, row, column, 1)  # 绘制棋子
            window.update()

            # 判断胜负
            if judge(game_board) == 1:
                tk.messagebox.showinfo("玩家胜利！")
                sys.exit()
            elif judge(game_board) == -1:
                tk.messagebox.showinfo("电脑胜利！")
                sys.exit()

            # AI行棋
            ai_row, ai_column = game_ai.ai_move(game_board, neighbourhood)
            assert 0 <= ai_row <= 14 and 0 <= ai_column <= 14 and game_board[ai_row][ai_column] == 0
            # 更新邻域
            try:
                neighbourhood[f(row - 1)][f(column - 1)] = \
                    neighbourhood[f(row)][f(column - 1)] = \
                    neighbourhood[f(row + 1)][f(column - 1)] = \
                    neighbourhood[f(row - 1)][f(column)] = \
                    neighbourhood[f(row + 1)][f(column)] = \
                    neighbourhood[f(row - 1)][f(column + 1)] = \
                    neighbourhood[f(row)][f(column + 1)] = \
                    neighbourhood[f(row + 1)][f(column + 1)] = 1
            except:
                pass
            game_board[ai_row][ai_column] = -1
            draw_pieces(canvas, ai_row, ai_column, -1)
            window.update()

            # 判断胜负
            if judge(game_board) == 1:
                tk.messagebox.showinfo("玩家胜利！")
                sys.exit()
            elif judge(game_board) == -1:
                tk.messagebox.showinfo("电脑胜利！")
                sys.exit()


canvas.bind('<Button-1>', onclick)
window.mainloop()
