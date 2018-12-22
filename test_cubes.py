#!/usr/bin/env python3

import unittest
import Field as b


class Test(unittest.TestCase):

    def test_steps(self):
        board = b.FieldState(2, 2)
        ans = False
        board.start_game()
        for x in range(len(board.board)):
            for y in range(len(board.board[0])):
                if len(board.logic.find_block(board.board, x, y)) > 1:
                    ans = True
                    break
        self.assertEqual(True, ans)

    def test_no_steps(self):
        board = b.FieldState(2, 2)
        board.board = [[1, 2], [2, 1]]
        ans = board.no_steps(board.board)
        self.assertEqual(True, ans)

    def test_shift_right(self):
        board = b.FieldState(2, 2)
        board.board = [[1, 1], [2, 2]]
        board.logic.shift(board.board, board.logic.find_block(board.board, 0, 0))
        excpected = [[2, 2]]
        ans = []
        for i in range(len(board.board)):
            ans.append([])
            for j in range(len(board.board[0])):
                ans[i].append(board.board[i][j])
        self.assertListEqual(excpected, ans)

    def test_shift_down(self):
        board = b.FieldState(2, 2)
        board.board = [[1, 2], [1, 2]]
        board.logic.shift(board.board, board.logic.find_block(board.board, 1, 1))
        excpected = [[1], [1]]
        ans = []
        for i in range(len(board.board)):
            ans.append([])
            for j in range(len(board.board[0])):
                ans[i].append(board.board[i][j])
        self.assertListEqual(excpected, ans)

    def test_count_blocks(self):
        board = b.FieldState(2, 2)
        board.board = [[1, 2], [1, 2]]
        board.count_blocks()
        excpected = [1, 1]
        ans = board.rest_block
        self.assertListEqual(excpected, ans)

if __name__ == '__main__':
    unittest.main()