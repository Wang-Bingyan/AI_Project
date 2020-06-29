# 游戏AI
import numpy as np

# 评分表
value_table = [

    # 成五
    [[1, 1, 1, 1, 1], 60001],
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
    def update_search_area(self, old_search_area, row, column):
        new_search_area = old_search_area.copy()
        new_search_area[self.__limit(row - 1)][self.__limit(column - 1)] = \
            new_search_area[self.__limit(row)][self.__limit(column - 1)] = \
            new_search_area[self.__limit(row + 1)][self.__limit(column - 1)] = \
            new_search_area[self.__limit(row - 1)][self.__limit(column)] = \
            new_search_area[self.__limit(row + 1)][self.__limit(column)] = \
            new_search_area[self.__limit(row - 1)][self.__limit(column + 1)] = \
            new_search_area[self.__limit(row)][self.__limit(column + 1)] = \
            new_search_area[self.__limit(row + 1)][self.__limit(column + 1)] = 1
        return new_search_area

    # 每次要更新棋盘时，必须通过这个函数。不要直接去修改self.board，因为更新棋盘的同时还要顺带更新utility
    # value的取值: -1, 0, 1
    def update_board(self, row, column, value):
        self.board[row][column] = value
        self.__update_utility(row, column)

    # 更新存储的效用值
    # 每下一步棋，就有4条线上的效用值会发生变化
    def __update_utility(self, row, column):
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

    # 返回当前self.board的效用值
    def __get_utility(self):
        return self.__utility_sum

    # min搜索
    def min_value(self, search_area, depth, alpha, beta):
        value = 114514
        if depth == 1:
            return self.__get_utility()
        else:
            for i in range(self.size):
                for j in range(self.size):
                    if search_area[i][j] == 1 and self.board[i][j] == 0:

                        # max走下一步棋
                        self.update_board(i, j, 1)
                        # 根据这一步棋，确定一个新的搜索域
                        new_search_area = self.update_search_area(search_area, i, j)
                        
                        # value = MIN(value, self.max_value(new_search_area, depth - 1, alpha, beta)
                        tmp = self.max_value(new_search_area, depth - 1, alpha, beta)

                        # 恢复board的状态
                        self.update_board(i, j, 0)

                        if tmp < value:
                            value = tmp
                        
                        # 剪枝
                        if value <= alpha:
                            self.update_board(i, j, 0)
                            return value

                        # 更新beta
                        if value <= beta:
                            beta = value
        return value

    # max搜索
    def max_value(self, search_area, depth, alpha, beta):
        value = -114514
        if depth == 1:
            return self.__get_utility()
        else:
            for i in range(self.size):
                for j in range(self.size):
                    if search_area[i][j] == 1 and self.board[i][j] == 0:

                        # min走下一步棋
                        self.update_board(i, j, -1)
                        # 根据这一步棋，确定一个新的搜索域
                        new_search_area = self.update_search_area(search_area, i, j)
                        
                        # value = MAX(value, self.min_value(new_search_area, depth - 1, alpha, beta)
                        tmp = self.min_value(new_search_area, depth - 1, alpha, beta)

                        # 恢复board的状态
                        self.update_board(i, j, 0)

                        if tmp > value:
                            value = tmp
                            
                        # 剪枝
                        if value >= beta:
                            return value
                        
                        # 更新alpha
                        if value >= alpha:
                            alpha = value
        return value
    
    # alpha-beta剪枝
    def alpha_beta_search(self, depth):
        
        row = column = self.size // 2
        value = 114514  # 初始化为正无穷

        # 调试用变量: 一个存储所有位置的value的矩阵
        value_board = np.full([self.size, self.size], np.nan)
        
        for i in range(self.size):
            for j in range(self.size):
                if self.search_area[i][j] == 1 and self.board[i][j] == 0:
                    # 假设先在这个位置下一步
                    self.update_board(i, j, -1)
                    # 计算出此时的min_value
                    tmp = self.min_value(self.search_area, depth, -1919810, 1919810)
                    value_board[i][j] = tmp
                    if tmp < value:
                        value = tmp
                        row = i
                        column = j
                    # 完成后，要把棋盘恢复原状
                    self.update_board(i, j, 0)
        # 调试
        print("===============================================")
        print(value_board)
        print("===============================================")
        
        return row, column
        
    # AI接口
    def ai_move(self):
        search_depth = 3  # 搜索深度
        return self.alpha_beta_search(search_depth)

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
        self.__utility_column = np.zeros([self.size], int)
        self.__utility_diagonal1 = np.zeros([2 * self.size - 1], int)
        self.__utility_diagonal2 = np.zeros([2 * self.size - 1], int)
        self.__utility_sum = 0
