from PyQt5 import QtCore
from copy import deepcopy
from Field import FieldState
from PyQt5.QtWidgets import QDesktopWidget, QPushButton, QDialog, QGridLayout, QLineEdit, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont, QPalette
import yaml
from cubes import Game


class NameRequest(QDialog):

    def __init__(self, scores, score, size, colors_number):
        super().__init__()
        self.scores = scores
        self.score = score
        self.size = size
        self.colors_number = colors_number

        q = QDesktopWidget().availableGeometry()
        self.resize(q.width() // 4, q.height() // 8)

        grid = QGridLayout()

        self.lbl_name = QLabel("Введите ваше имя", self)
        grid.addWidget(self.lbl_name, 0, 0)
        self.name_box = QLineEdit(self)
        grid.addWidget(self.name_box, 1, 0)
        self.button = QPushButton('OK', self)
        grid.addWidget(self.button, 2, 0)
        self.button.clicked.connect(self.on_click)

        self.setLayout(grid)


    def on_click(self):
        self.name = self.name_box.text()

        if self.name != "":
            self.close()
            self.res = ResultPainter(self.name, self.scores, self.score, self.size, self.colors_number)
            self.res.show()


class ResultPainter(QDialog):
    def __init__(self, name, score_table, score, size, number_of_colors):
        super().__init__()
        self.score = score
        self.size = size
        self.number_of_colors = number_of_colors
        self.name = name
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.score_table = score_table
        q = QDesktopWidget().availableGeometry()
        self.resize(q.width() // 2, q.height() // 2)
        ScoresTable().add(self.name, self.score, self.size, self.number_of_colors)

    def paintEvent(self, e):

        painter = QPainter()
        painter.begin(self)
        self.draw_results(painter)
        painter.end()

    def draw_results(self, painter):
        grid = QGridLayout()
        size = "{}*{}".format(self.size, self.size)
        results = []
        first = True
        for i in range(8):
            if self.score_table.score_table[size][self.number_of_colors][i]["score"] <= self.score and first:
                results.append((self.name, self.score))
                first = False
            results.append((self.score_table.score_table[size][self.number_of_colors][i]["name"],
                            self.score_table.score_table[size][self.number_of_colors][i]["score"]))
        if first:
            results.append((self.name, self.score))
        main_label = QLabel("SCORE TABLE", self)
        grid.addWidget(main_label, 0, 0)
        main_label.setFont(QFont("Times", 12, QFont.Bold))
        i = 1
        first = True
        for name, score in results:
            if name == "":
                break
            label_name = QLabel(name, self)
            label_score = QLabel(str(score), self)
            label_name.setFont(QFont("Times", 10, QFont.Bold))
            label_score.setFont(QFont("Times", 10, QFont.Bold))
            if name == self.name and score == self.score and first:
                first = False
                label_name.setStyleSheet("QLabel { color: red}")
                label_score.setStyleSheet("QLabel { color: red}")

            grid.addWidget(label_name, i, 0)
            grid.addWidget(label_score, i, 1)
            i += 1
        self.new_game_btn = QPushButton('NEW\nGAME', self)
        grid.addWidget(self.new_game_btn, 0, 2)
        self.new_game_btn.clicked.connect(self.new_game)

        self.setLayout(grid)
        self.show()

    def new_game(self):
        self.close()
        self.game = Game()


class ScoresTable:
    SCORE_TABLE_FILE_NAME = 'scoreTable.yaml'
    TABLE_SIZE = 8

    def __init__(self):

        with open(self.SCORE_TABLE_FILE_NAME) as f:
            self.score_table = yaml.load(f)

    def add(self, name, score, size, number_of_colors):
        size = "{}*{}".format(size, size)
        score_tbl = deepcopy(self.score_table)
        for i in range(self.TABLE_SIZE):
            if score_tbl[size][number_of_colors][i]["score"] <= score:
                score_tbl[size][number_of_colors].insert(i, {"name": name, "score": score})
                score_tbl[size][number_of_colors] = score_tbl[size][number_of_colors][:8]
                break
        with open(self.SCORE_TABLE_FILE_NAME, 'w') as f:
            yaml.dump(score_tbl, f)


class Board(QDialog):
    COLOR_TABLE = [0xFFFFFF, 0x66CC00, 0x7788BB, 0x9977AA,
                   0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00,
                   0xCC0000, 0x6C00DD, 0x00DDFF]

    def __init__(self, tbl_size, colors):
        super().__init__()
        q = QDesktopWidget().availableGeometry()
        self.cube_side = min(q.height() // (2 + tbl_size), q.width() // (3 + tbl_size))
        self.field = FieldState(tbl_size, colors)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setMouseTracking(True)
        self.undo_btn = QPushButton('UNDO', self)
        self.undo_btn.move(self.cube_side * tbl_size, self.cube_side * 2)
        self.undo_btn.resize(self.cube_side, self.cube_side)
        self.undo_btn.clicked.connect(self.undo)
        self.rendo_btn = QPushButton('RENDO', self)
        self.rendo_btn.move(self.cube_side * tbl_size, self.cube_side)
        self.rendo_btn.resize(self.cube_side, self.cube_side)
        self.rendo_btn.clicked.connect(self.rendo)
        self.restart_btn = QPushButton('RESTART', self)
        self.restart_btn.move(self.cube_side * (1 + tbl_size), self.cube_side)
        self.restart_btn.resize(self.cube_side, self.cube_side)
        self.restart_btn.clicked.connect(self.restart)
        self.new_game_btn = QPushButton('NEW\nGAME', self)
        self.new_game_btn.move(self.cube_side * (1 + tbl_size), 2 * self.cube_side)
        self.new_game_btn.resize(self.cube_side, self.cube_side)
        self.new_game_btn.clicked.connect(self.new_game)
        self.scores = ScoresTable()
        size = "{}*{}".format(self.field.tbl_size, self.field.tbl_size)
        self.best_score = QLabel(
            "Best result:\n" + str(self.scores.score_table[size][self.field.colors_number][0]["score"]), self)
        if self.scores.score_table[size][self.field.colors_number][0]["score"] == 0:
            self.best_score.setText('')
        self.best_score.move(self.cube_side * (2 + tbl_size), 0)
        self.best_score.resize(self.cube_side, self.cube_side)
        self.total_score = QLabel('Total:\n' + str(self.field.score), self)
        self.total_score.move(self.cube_side * (1 + tbl_size), 0)
        self.total_score.resize(self.cube_side, self.cube_side)
        self.cur_price = QLabel('', self)
        self.cur_price.move(self.cube_side * tbl_size, 0)
        self.cur_price.resize(self.cube_side, self.cube_side)

        blocks_number = QLabel('Number of blocks:', self)
        blocks_number.move(0, self.cube_side * self.field.tbl_size)
        blocks_number.resize(self.cube_side * 3, self.cube_side)

    def new_game(self):
        self.close()
        self.game = Game()

    def mousePressEvent(self, event):
        y = self.field.tbl_size - 1 - event.pos().y() // self.cube_side
        x = event.pos().x() // self.cube_side
        if y < self.field.tbl_size and x < self.field.tbl_size:
            to_delete = self.field.logic.find_block(self.field.board, x, y)
            if len(to_delete) >= 2:
                self.field.score += self.field.count_score(len(to_delete))
                self.field.logic.shift(self.field.board, to_delete)
                self.total_score.setText('Total:\n' + str(self.field.score))
                if self.field.no_steps():
                    self.field.is_started = False
            if 0 <= x < len(self.field.board) and 0 <= y < len(self.field.board[x]):
                to_delete = self.field.logic.find_block(self.field.board, x, y)
                if len(to_delete) < 2:
                    self.field.make_lighter = (False, [])
                else:
                    self.field.make_lighter = (True, to_delete)
            else:
                self.field.make_lighter = (False, [])
            self.field.previous.append((deepcopy(self.field.board), deepcopy(self.field.score)))
            self.field.next = []
            self.field.count_blocks()
            self.update()


    def paintEvent(self, event):
        self.cur_score = str(self.field.score)
        painter = QPainter(self)
        for i in range(self.field.tbl_size):
            for j in range(self.field.tbl_size - 1, -1, -1):
                x = self.contentsRect().left() + j * self.cube_side
                y = (self.field.tbl_size - 1 - i) * self.cube_side
                if len(self.field.board) > j >= 0 and 0 <= i < len(self.field.board[j]):
                    painter.fillRect(x, y,
                                 self.cube_side - 5,
                                 self.cube_side - 5,
                                 QColor(self.COLOR_TABLE[self.field.board[j][i]]))
                else:
                    painter.fillRect(x, y,
                                 self.cube_side - 5,
                                 self.cube_side - 5,
                                 QColor(self.COLOR_TABLE[0]))

        if self.field.make_lighter[0]:
            for k in self.field.make_lighter[1]:
                painter.fillRect(k[0] * self.cube_side, (self.field.tbl_size - 1 - k[1]) * self.cube_side,
                                 self.cube_side - 5,
                                 self.cube_side - 5,
                                 QColor(self.COLOR_TABLE[self.field.board[k[0]][k[1]]]).lighter())
            self.cur_price.setText('Price: ' + str(self.field.count_score(len(self.field.make_lighter[1]))))
        else:
            self.cur_price.setText('')
        painter.setFont(QFont('Decorative', self.cube_side // 4))
        for i in range(self.field.colors_number):
            painter.setPen(QColor(self.COLOR_TABLE[i + 1]))
            painter.drawText(i * self.cube_side, self.cube_side * (2 + self.field.tbl_size),
                             str(self.field.rest_block[i]))

        if not self.field.is_started:
            self.close()
            self.name_request = NameRequest(deepcopy(self.scores), self.field.score, self.field.tbl_size, self.field.colors_number)
            self.name_request.show()

    def mouseMoveEvent(self, event):
        y = self.field.tbl_size - 1 - event.pos().y() // self.cube_side
        x = event.pos().x() // self.cube_side
        if 0 <= x < len(self.field.board) and 0 <= y < len(self.field.board[x]):
            to_delete = self.field.logic.find_block(self.field.board, x, y)
            if len(to_delete) < 2:
                self.field.make_lighter = (False, [])
            else:
                self.field.make_lighter = (True, to_delete)
        else:
            self.field.make_lighter = (False, [])
        self.update()

    def undo(self):
        self.field.undo()
        self.update()

    def rendo(self):
        self.field.rendo()
        self.update()

    def restart(self):
        self.field.is_started = True
        self.field.score = 0
        self.field.make_lighter = (False, [])
        self.field.board = deepcopy(self.field.start_board)
        self.field.previous = []
        self.field.next = []
        self.update()

