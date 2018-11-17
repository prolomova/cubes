import random
from copy import deepcopy
import functools


class Logic:
    def __init__(self):
        pass

    def find_block(self, board, x, y, block = None):
        if not block:
            block = {(x, y)}
        if len(board) <= x < 0 or 0 > y >= len(board[x]):
            return []
        for i, j in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if len(board) > i + x >= 0 \
              and 0 <= j + y < len(board[i + x]):
                if board[i + x][y + j] ==\
                        board[x][y] \
                  and (i + x, y + j) not in block:
                    block.add((i + x, y + j))
                    self.find_block(board, i + x, j + y, block)
        return list(block)

    def shift(self, board, to_delete):
        to_delete.sort(key=lambda x: x[1], reverse=True)
        to_delete.sort(key=lambda x: x[0], reverse=True)
        for cell in to_delete:
            board[cell[0]].pop(cell[1])
        for i in range(len(board) - 1, -1, -1):
            if not board[i]:
                board.pop(i)


class FieldState:
    def __init__(self, tbl_size, colors):
        self.start_board = []
        self.score = 0
        self.colors_number = colors
        self.tbl_size = tbl_size
        self.make_lighter = (False, [])
        self.board = []
        self.previous = []
        self.next = []
        self.is_started = False
        self.logic = Logic()
        self.rest_block = []

    @functools.lru_cache()
    def count_score(self, n):

        if n + 1 < 3:
            return 0
        if n + 1 < 6:
            return [1, 3, 5][n - 2]

        return self.count_score(n - 1) + self.count_score(n - 2)

    def start_game(self):
        self.is_started = True
        self.score = 0
        self.make_lighter = (False, [])
        self.previous = []
        self.next = []
        self.board = []
        self.init_board()
        self.count_blocks()
        self.start_board = deepcopy(self.board)

    def init_board(self):
        for i in range(self.tbl_size):
            self.board.append([])
            for j in range(self.tbl_size):
                self.board[i].append(self.get_random_color())
        if self.no_steps():
            self.board[0][0] = self.board[0][1 % self.tbl_size]
        self.previous.append((deepcopy(self.board), deepcopy(self.score)))
        self.next = []

    def count_blocks(self):
        self.rest_block = [0] * self.colors_number
        proved_board = []
        for i in range(len(self.board)):
            proved_board.append([False] * len(self.board[i]))
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if not proved_board[i][j]:
                    block = self.logic.find_block(self.board, i, j)
                    for x, y in block:
                        proved_board[x][y] = True
                    if len(block) >= 2:
                        self.rest_block[self.board[i][j] - 1] += 1


    def get_random_color(self):
        return random.randint(1, self.colors_number)

    def no_steps(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if len(self.logic.find_block(self.board, i, j)) >= 2:
                    return False
        return True

    def undo(self):
        if len(self.previous) >= 2 and self.is_started:
            self.next.append(deepcopy(self.previous.pop()))
            previous = deepcopy(self.previous[-1])
            self.board = deepcopy(previous[0])

    def rendo(self):
        if len(self.next) >= 1 and self.is_started:
            next = deepcopy(self.next[-1])
            self.board = deepcopy(next[0])
            self.score = deepcopy(next[1])
            self.previous.append(deepcopy(self.next.pop()))