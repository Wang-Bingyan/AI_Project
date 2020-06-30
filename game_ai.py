# 游戏AI
import numpy as np
import AhoCorasick

# 评分表
value_table = {
    # B - 黑棋，W - 白棋， O - 空位

    # 成五（五个一线）
    "BBBBB": 50000,
    "WWWWW": -50000,
    # 活四（有两个位置可以成五）
    "OBBBBO": 10000,
    "OWWWWO": -10000,
    # 冲四（有一个位置可以成五）
    "OBBBB": 5000,
    "OWWWW": -5000,
    "BBBBO": 5000,
    "WWWWO": -5000,
    "BOBBB": 5000,
    "WOWWW": -5000,
    "BBBOB": 5000,
    "WWWOW": -5000,
    "BBOBB": 5000,
    "WWOWW": -5000,
    # 活三（有两个位置可以变成活四）
    "OBBBO": 2000,
    "OWWWO": -2000,
    # 有一个位置可以变成活四
    "OBBOBO": 1800,
    "OWWOWO": -1800,
    # 冲三(有一个位置可以变成冲四)
    "OBBB": 400,
    "OWWW": -400,
    "BBBO": 400,
    "WWWO": -400,
    "BOBOB": 400,
    "WOWOW": -400,
    # 活二(有两个位置可以变成活三)
    "OBBOO": 400,
    "OWWOO": -400,
    "OOBBO": 400,
    "OOWWO": -400,
    "OOBOBO": 400,
    "OOWOWO": -400,
    "OBOBOO": 400,
    "OWOWOO": -400,
    # 活一
    "OOBOO": 50,
    "OOWOO": -50
}


def tostring(line):
    d = {1: "B", -1: "W", 0: "O"}
    s = ""
    for i in line:
        s += d[i]
    return s


class AI(object):

    # 用于防止数组越界
    def __limit(self, n):
        if n < 0:
            return 0
        if n >= self.size:
            return self.size - 1
        else:
            return n

    # 评估一条线上的棋形
    def utility_line(self, line):
        line_string = tostring(line)

        # 检查是否缓存了这条线的值
        if line_string in self.__line_dict:
            return self.__line_dict[line_string]

        # 如果没有，则计算一次
        t = self.ac.search(line_string)
        vs = [value_table[i] for i in t]
        if not vs:
            return 0
        v1 = max(vs)
        v2 = min(vs)
        if abs(v1) > abs(v2):
            value = v1
        else:
            value = v2
        self.__line_dict[line_string] = value  # 储存结果
        return value

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
        u_r = self.utility_line(self.board[row])
        u_c = self.utility_line(self.board[:, column])
        # 对角线真烦人
        u_d1 = self.utility_line(self.board.diagonal(offset=column - row))
        mirror = np.fliplr(self.board)
        u_d2 = self.utility_line(mirror.diagonal(offset=self.size - row - column - 1))

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
        row = column = 0
        if depth == 1 or self.game_judge() != 0:
            return self.__get_utility(), 0, 0
        else:
            for i in range(self.size):
                for j in range(self.size):
                    if search_area[i][j] == 1 and self.board[i][j] == 0:

                        # min走下一步棋
                        self.update_board(i, j, -1)
                        # 根据这一步棋，确定一个新的搜索域
                        new_search_area = self.update_search_area(search_area, i, j)
                        
                        # value = MIN(value, self.max_value(new_search_area, depth - 1, alpha, beta)
                        tmp, _, _ = self.max_value(new_search_area, depth - 1, alpha, beta)
                        if tmp < value:
                            value = tmp
                            row = i
                            column = j

                        # 恢复board的状态
                        self.update_board(i, j, 0)
                        
                        # 剪枝
                        if value <= alpha:
                            return value, row, column

                        beta = min(beta, value)
        return value, row, column

    # max搜索
    def max_value(self, search_area, depth, alpha, beta):
        value = -114514
        row = column = 0
        if depth == 1 or self.game_judge() != 0:
            return self.__get_utility(), 0, 0
        else:
            for i in range(self.size):
                for j in range(self.size):
                    if search_area[i][j] == 1 and self.board[i][j] == 0:

                        # max走下一步棋
                        self.update_board(i, j, 1)
                        # 根据这一步棋，确定一个新的搜索域
                        new_search_area = self.update_search_area(search_area, i, j)

                        # value = MAX(value, self.min_value(new_search_area, depth - 1, alpha, beta)
                        tmp, _, _ = self.min_value(new_search_area, depth - 1, alpha, beta)
                        if tmp > value:
                            value = tmp
                            row = i
                            column = j

                        # 恢复board的状态
                        self.update_board(i, j, 0)
                            
                        # 剪枝
                        if value >= beta:
                            return value, row, column
                        
                        # 更新alpha
                        alpha = max(alpha, value)
        return value, row, column
    
    # alpha-beta剪枝
    def alpha_beta_search(self, depth):
        _, row, column = self.min_value(self.search_area, depth, -1919810, 1919810)
        return row, column

    def game_judge(self):
        board_t = self.board.transpose()
        board_mirror = np.flip(self.board, 0)
        # 行与列
        for i in range(15):
            for j in range(11):
                # 5个一行
                if (self.board[i][j: j + 5] == [1, 1, 1, 1, 1]).all():
                    return 1
                elif (self.board[i][j: j + 5] == [-1, -1, -1, -1, -1]).all():
                    return -1
                # 5个一列
                if (board_t[i][j: j + 5] == [1, 1, 1, 1, 1]).all():
                    return 1
                elif (board_t[i][j: j + 5] == [-1, -1, -1, -1, -1]).all():
                    return -1
        # 对角线
        for i in range(11):
            for j in range(11):
                if self.board[i][j] == 1 and self.board[i + 1][j + 1] == 1 and self.board[i + 2][j + 2] == 1 \
                        and self.board[i + 3][j + 3] == 1 and self.board[i + 4][j + 4] == 1:
                    return 1
                elif self.board[i][j] == -1 and self.board[i + 1][j + 1] == -1 and self.board[i + 2][j + 2] == -1 \
                        and self.board[i + 3][j + 3] == -1 and self.board[i + 4][j + 4] == -1:
                    return -1
                if board_mirror[i][j] == 1 and board_mirror[i + 1][j + 1] == 1 and board_mirror[i + 2][j + 2] == 1 \
                        and board_mirror[i + 3][j + 3] == 1 and board_mirror[i + 4][j + 4] == 1:
                    return 1
                elif board_mirror[i][j] == -1 and board_mirror[i + 1][j + 1] == -1 and board_mirror[i + 2][j + 2] == -1 \
                        and board_mirror[i + 3][j + 3] == -1 and board_mirror[i + 4][j + 4] == -1:
                    return -1
        return 0
        
    # AI接口
    def ai_move(self):
        search_depth = 4  # 搜索深度
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

        # 缓存效用值，避免计算第二次
        self.__line_dict = {}

        # AC自动机初始化
        self.ac = AhoCorasick.AhoCorasick(set(value_table.keys()))
