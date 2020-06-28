# 游戏AI
import numpy as np
import random

# 评分表
value_table = [

    # 成五
    [[1, 1, 1, 1, 1], 50001],
    [[-1, -1, -1, -1, -1], -50000],

    # 活四
    [[0, 1, 1, 1, 1, 0], 4321],
    [[0, -1, -1, -1, -1, 0], -4320],

    # 冲四
    [[1, 1, 1, 1, 0], 1441],
    [[-1, -1, -1, -1, 0], -1440],
    [[0, 1, 1, 1, 1], 1441],
    [[0, -1, -1, -1, -1], -1440],
    [[1, 1, 0, 1, 1], 1441],
    [[-1, -1, 0, -1, -1], -1440],
    [[1, 0, 1, 1, 1], 1441],
    [[-1, 0, -1, -1, -1], -1440],
    [[1, 1, 1, 0, 1], 1441],
    [[-1, -1, -1, 0, -1], -1440],

    # 活三
    [[0, 1, 1, 1, 0], 721],
    [[0, -1, -1, -1, 0], -720],
    [[0, 1, 1, 1, 0], 721],
    [[0, -1, -1, -1, 0], -720],

    [[0, 1, 1, 0, 1, 0], 721],
    [[0, -1, -1, 0, -1, 0], -720],

    [[0, 1, 0, 1, 1, 0], 721],
    [[0, -1, 0, -1, -1, 0], -720],

    # 活二
    [[0, 0, 1, 1, 0, 0], 121],
    [[0, 0, -1, -1, 0, 0], -120],

    [[0, 0, 1, 0, 1, 0], 121],
    [[0, 0, -1, 0, -1, 0], -120],

    [[0, 1, 0, 1, 0, 0], 121],
    [[0, -1, 0, -1, 0, 0], -120],

    [[0, 0, 1, 0, 0], 21],
    [[0, 0, -1, 0, 0], -20],

    [[0, 0, 1, 0, 0], 21],
    [[0, 0, -1, 0, 0], -20],
]


# 评估一条线上的棋形
def utility_line(line):
    if type(line) == int or len(line) < 5:
        return 0
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


class AI(object):

    # 用于防止数组越界
    def __limit(self, n):
        if n < 0:
            return 0
        if n >= self.size:
            return self.size - 1
        else:
            return n

    # 更新搜索域，每当落下一颗棋子时，将它周围的8个位置设为搜索域
    def update_search_area(self, row, column):
        self.search_area[self.__limit(row - 1)][self.__limit(column - 1)] = \
            self.search_area[self.__limit(row)][self.__limit(column - 1)] = \
            self.search_area[self.__limit(row + 1)][self.__limit(column - 1)] = \
            self.search_area[self.__limit(row - 1)][self.__limit(column)] = \
            self.search_area[self.__limit(row + 1)][self.__limit(column)] = \
            self.search_area[self.__limit(row - 1)][self.__limit(column + 1)] = \
            self.search_area[self.__limit(row)][self.__limit(column + 1)] = \
            self.search_area[self.__limit(row + 1)][self.__limit(column + 1)] = 1

    # 更新存储的效用值
    def update_utility(self, row, column):
        u_r = utility_line(self.board[row])
        u_c = utility_line(self.board[:, column])
        # 对角线真烦人
        u_d1 = utility_line(self.board.diagonal(offset=column - row))
        mirror = np.fliplr(self.board)
        u_d2 = utility_line(mirror.diagonal(offset=self.size - row - column - 1))

        self.__utility_sum += u_r - self.__utility_row[row] + u_c - self.__utility_column[column] + \
            u_d1 - self.__utility_diagonal1[column - row + self.size - 1] + \
            u_d2 - self.__utility_diagonal2[2 * self.size - row - column - 2]

        self.__utility_row[row] = u_r
        self.__utility_column[column] = u_c
        self.__utility_diagonal1[column - row + self.size - 1] = u_d1
        self.__utility_diagonal2[2 * self.size - row - column - 2] = u_d2

    # 下在i行j列时的效用值
    def utility(self, player, i, j):
        self.board[i][j] = player
        mirror = np.fliplr(self.board)
        value = self.__utility_sum + \
            utility_line(self.board[i]) + \
            utility_line(self.board[:, j]) + \
            utility_line(self.board.diagonal(offset=j - i)) + \
            utility_line(mirror.diagonal(offset=self.size - i - j - 1))
        value -= self.__utility_row[i] + self.__utility_column[j] + \
            self.__utility_diagonal1[j - i + self.size - 1] + self.__utility_diagonal2[2 * self.size - i - j - 2]
        self.board[i][j] = 0
        return value

    # AI接口
    def ai_move(self):
        size = np.size(self.board, 0)
        row = size // 2
        column = size // 2
        min_value = 114514

        # ================= 算法实现 =================
        for i in range(size):
            for j in range(size):
                if self.search_area[i][j] == 1 and self.board[i][j] == 0:
                    utility = self.utility(-1, i, j)
                    if utility < min_value:
                        row = i
                        column = j
                        min_value = utility

        # 测试用
        # ===========================================
        print("=====================================")

        tmp = np.full([self.size, self.size], -1)

        for i in range(size):
            for j in range(size):
                if self.search_area[i][j] == 1 and self.board[i][j] == 0:
                    tmp[i][j] = self.utility(-1, i, j)
        print(tmp)
        print("=====================================")

        return row, column

    # 初始化
    def __init__(self, board):
        self.board = board
        self.size = np.size(board[0])
        self.search_area = np.zeros([self.size, self.size], int)  # 搜索域
        # 这几个字段的作用是存储每一行，每一列，每一对角线的效用值
        # 之所以这样做，是因为：每下一步棋只会改变棋子所在的行、列、对角线的效用值
        # 而之前的算法每次都要重新计算整个棋盘，效率很低
        # 因此改为分开存储每一行、列、对角线的效用值，每下一步棋后调用 update_utility 更新一次
        # 这样就大大减少了计算量
        self.__utility_row = np.zeros([self.size], int)
        self.__utility_column = np.zeros([self.size])
        self.__utility_diagonal1 = np.zeros([2 * self.size - 1])
        self.__utility_diagonal2 = np.zeros([2 * self.size - 1])
        self.__utility_sum = 0
