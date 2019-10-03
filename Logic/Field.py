import random
from copy import deepcopy
import functools


class Logic:
    def __init__(self):
        pass

    def find_block(self, board, x, y, block=None):
        if not block:
            block = {(x, y)}
        if len(board) <= x or x < 0 or 0 > y or y >= len(board[x]):
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
    def __init__(self, height, width, colors):
        self.start_board = []
        self.max_score = 0
        self.score = 0
        self.colors_number = colors
        self.height = height
        self.width = width
        self.make_lighter = (False, [])
        self.board = []
        self.previous = []
        self.next = []
        self.is_started = False
        self.logic = Logic()
        self.rest_block = []
        self.stop_calculating = False

    @functools.lru_cache()
    def count_score(self, n):

        if n + 1 < 3:
            return 0
        if n + 1 < 6:
            return [1, 3, 5][n - 2]

        return self.count_score(n - 1) + self.count_score(n - 2)

    def start_game(self):
        self.max_score = 0
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
        for i in range(self.width):
            self.board.append([])
            for j in range(self.height):
                self.board[i].append(self.get_random_color())
        if self.no_steps(self.board):
            self.board[0][0] = self.board[0][1 % self.height]
        self.previous.append(
            (deepcopy(self.board), self.score, self.max_score))
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

    def no_steps(self, board):
        for i in range(len(board)):
            for j in range(len(board[i])):
                if len(self.logic.find_block(board, i, j)) >= 2:
                    return False
        return True

    def undo(self):
        if len(self.previous) >= 2 and self.is_started:
            self.next.append(deepcopy(self.previous.pop()))
            previous = deepcopy(self.previous[-1])
            self.board = deepcopy(previous[0])
            self.max_score = previous[2]
            self.score = previous[1]

    def rendo(self):
        if len(self.next) >= 1 and self.is_started:
            next = deepcopy(self.next[-1])
            self.previous.append(deepcopy(self.next.pop()))
            self.board = deepcopy(next[0])
            self.score = deepcopy(next[1])
            self.max_score = deepcopy(next[2])

    def count_possible_score(self, new_board, init_score):
        while not self.stop_calculating:
            board = deepcopy(new_board)
            score = init_score
            while not self.no_steps(board):
                x = random.randint(0, len(board))
                if x >= len(board):
                    continue
                y = random.randint(0, len(board[x]))
                to_delete = self.logic.find_block(board, y, x)
                if len(to_delete) >= 2:
                    n = self.count_score(len(to_delete))
                    self.logic.shift(board, to_delete)
                    score += n
                    self.max_score = max(self.max_score, score)
            self.max_score = max(self.max_score, score)
