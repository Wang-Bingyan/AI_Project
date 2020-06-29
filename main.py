# 图形界面
import tkinter as tk
import tkinter.messagebox
import numpy as np
import sys

import game_ai


class Game(object):
    # 初始化
    def __init__(self):
        self.window = tk.Tk()
        self.window.resizable(width=False, height=False)
        self.window.title('五子棋')

        self.line_width = 3  # 一根线的宽度
        self.grid_width = 40  # 一个格子的宽度
        self.border_width = 40  # 边界的宽度
        self.size = 15 * self.line_width + 14 * self.grid_width + 2 * self.border_width  # 尺寸

        # 绘制棋盘
        self.canvas = tk.Canvas(self.window, background='white', width=self.size, height=self.size)
        self.img_board = tk.PhotoImage(file="images/board.png")
        self.img_piece_black = tk.PhotoImage(file="images/piece_black.png")
        self.img_piece_white = tk.PhotoImage(file="images/piece_white.png")
        self.canvas.create_image(self.size // 2, self.size // 2, image=self.img_board)
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.onclick)

        self.game_board = np.zeros([15, 15], int)  # 棋盘用numpy数组表示
        self.ai = game_ai.AI(self.game_board)  # AI初始化

    # 绘制棋子，row和col代表棋子所在的列，player=1代表黑棋，player=-1代表白棋
    def draw_pieces(self, row, column, player):
        pos_x = self.border_width + self.line_width // 2 + 1 + (self.grid_width + self.line_width) * column
        pos_y = self.border_width + self.line_width // 2 + 1 + (self.grid_width + self.line_width) * row
        if player == 1:  # 黑棋
            self.canvas.create_image(pos_x, pos_y, image=self.img_piece_black)
        elif player == -1:  # 白棋
            self.canvas.create_image(pos_x, pos_y, image=self.img_piece_white)

    # 玩家行棋一步，开始一个回合
    def round(self, player_row, player_column):
        self.ai.update_board(player_row, player_column, 1)  # 更新棋盘
        self.draw_pieces(player_row, player_column, 1)  # 画出玩家的棋子
        self.window.update()  # 刷新屏幕

        # 胜负判断
        if self.game_judge() == 1:
            win_message(1)
            sys.exit()
        elif self.game_judge() == -1:
            win_message(-1)
            sys.exit()

        # 更新AI的搜索域
        self.ai.search_area = self.ai.update_search_area(self.ai.search_area, player_row, player_column)

        # AI行棋
        ai_row, ai_column = self.ai.ai_move()
        # 确认一下是否下到了合法的位置
        assert 0 <= ai_row <= 14 and 0 <= ai_column <= 14 and self.game_board[ai_row][ai_column] == 0

        self.ai.update_board(ai_row, ai_column, -1)  # 更新棋盘
        self.draw_pieces(ai_row, ai_column, -1)  # 画出AI的棋子
        self.window.update()  # 刷新屏幕

        # 胜负判断
        if self.game_judge() == 1:
            win_message(1)
            sys.exit()
        elif self.game_judge() == -1:
            win_message(-1)
            sys.exit()

        # 更新AI的搜索域
        self.ai.search_area = self.ai.update_search_area(self.ai.search_area, ai_row, ai_column)

    # 判断游戏胜负，1代表玩家胜利，-1代表电脑胜利，0代表无人胜利
    def game_judge(self):
        board_t = self.game_board.transpose()
        board_mirror = np.flip(self.game_board, 0)
        # 行与列
        for i in range(15):
            for j in range(11):
                # 5个一行
                if (self.game_board[i][j: j + 5] == [1, 1, 1, 1, 1]).all():
                    return 1
                elif (self.game_board[i][j: j + 5] == [-1, -1, -1, -1, -1]).all():
                    return -1
                # 5个一列
                if (board_t[i][j: j + 5] == [1, 1, 1, 1, 1]).all():
                    return 1
                elif (board_t[i][j: j + 5] == [-1, -1, -1, -1, -1]).all():
                    return -1
        # 对角线
        for i in range(11):
            for j in range(11):
                if self.game_board[i][j] == 1 and self.game_board[i + 1][j + 1] == 1 and self.game_board[i + 2][j + 2] == 1 \
                        and self.game_board[i + 3][j + 3] == 1 and self.game_board[i + 4][j + 4] == 1:
                    return 1
                elif self.game_board[i][j] == -1 and self.game_board[i + 1][j + 1] == -1 and self.game_board[i + 2][j + 2] == -1 \
                        and self.game_board[i + 3][j + 3] == -1 and self.game_board[i + 4][j + 4] == -1:
                    return -1
                if board_mirror[i][j] == 1 and board_mirror[i + 1][j + 1] == 1 and board_mirror[i + 2][j + 2] == 1 \
                        and board_mirror[i + 3][j + 3] == 1 and board_mirror[i + 4][j + 4] == 1:
                    return 1
                elif board_mirror[i][j] == -1 and board_mirror[i + 1][j + 1] == -1 and board_mirror[i + 2][j + 2] == -1 \
                        and board_mirror[i + 3][j + 3] == -1 and board_mirror[i + 4][j + 4] == -1:
                    return -1
        return 0

    # 鼠标事件
    def onclick(self, event):
        column = (event.x - self.border_width // 2) // (self.line_width + self.grid_width)
        row = (event.y - self.border_width // 2) // (self.line_width + self.grid_width)
        if 0 <= row <= 14 and 0 <= column <= 14 and self.game_board[row][column] == 0:
            self.round(row, column)

    # 游戏启动
    def start(self):
        self.window.mainloop()


def win_message(player):
    if player == 1:
        tk.messagebox.showinfo("胜利", "玩家胜利!")
    elif player == -1:
        tk.messagebox.showinfo("胜利", "AI胜利！")

  
if __name__ == "__main__":
    Game = Game()
    Game.start()
