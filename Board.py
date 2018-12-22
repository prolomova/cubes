from PyQt5 import QtCore
from copy import deepcopy
from PyQt5.QtWidgets import QDesktopWidget, QPushButton, QDialog, QGridLayout, QLineEdit, QLabel, QMainWindow
from PyQt5.QtGui import QPainter, QColor, QFont, QPalette
import yaml
from Field import FieldState, Logic
from cubes import Game
from threading import Thread
import time
from queue import Queue



class NameRequest(QDialog):

    def __init__(self):
        super().__init__()

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
        self.is_pushed = False
        self.setLayout(grid)
        self.show()

    def on_click(self):
        self.name = self.name_box.text()

        if self.name != "":
            self.is_pushed = True
            self.close()


class ResultPainter(QDialog):
    def __init__(self, name, score_table, score, height, width, number_of_colors):
        super().__init__()
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.score = score
        self.height = height
        self.width = width
        self.number_of_colors = number_of_colors
        self.name = name
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.score_table = score_table
        q = QDesktopWidget().availableGeometry()
        self.resize(q.width() // 2, q.height() // 2)
        ScoresTable().add(self.name, self.score, self.height, self.width, self.number_of_colors)

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        self.draw_results(painter)
        painter.end()



    def draw_results(self, painter):
        size = "{}*{}".format(self.height, self.width)
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
        self.grid.addWidget(main_label, 0, 0)
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

            self.grid.addWidget(label_name, i, 0)
            self.grid.addWidget(label_score, i, 1)
            i += 1
        self.new_game_btn = QPushButton('NEW\nGAME', self)
        self.grid.addWidget(self.new_game_btn, 0, 2)
        self.new_game_btn.clicked.connect(self.new_game)

        self.show()

    def new_game(self):
        self.close()
        self.game = Game(self.name)


class ScoresTable:
    SCORE_TABLE_FILE_NAME = 'scoreTable.yaml'
    TABLE_SIZE = 8

    def __init__(self):
        self.score_table = {}
        try:
            with open(self.SCORE_TABLE_FILE_NAME) as f:
                self.score_table = yaml.load(f)
        except:
            sizes = {'6*6': range(2, 7), '30*30': range(4, 11),
                     '15*15': range(2, 7), '12*12': range(2, 7)}
            for key, value in sizes.items():
                self.score_table[key] = {}
                for colors in value:
                    self.score_table[key][colors] = []
                    for _ in range(8):
                        self.score_table[key][colors].append({'name': '', 'score': 0})
            with open(self.SCORE_TABLE_FILE_NAME, 'w') as f:
                yaml.dump(self.score_table, f)


    def add(self, name, score, height, width, number_of_colors):
        size = "{}*{}".format(height, width)
        score_tbl = deepcopy(self.score_table)
        for i in range(self.TABLE_SIZE):
            if score_tbl[size][number_of_colors][i]["score"] <= score:
                score_tbl[size][number_of_colors].insert(i, {"name": name, "score": score})
                score_tbl[size][number_of_colors] = score_tbl[size][number_of_colors][:8]
                break
        with open(self.SCORE_TABLE_FILE_NAME, 'w') as f:
            yaml.dump(score_tbl, f)


class NewGameOptions(QDialog):
    def __init__(self, name, height = None, width = None, colors = None):
        super().__init__()
        self.height = height
        self.width = width
        self.colors = colors
        self.name = name
        q = QDesktopWidget().availableGeometry()
        self.resize(q.width() // 4, q.height() // 8)

        grid = QGridLayout()

        self.button = QPushButton('NEW\nGAME', self)
        grid.addWidget(self.button, 1, 0)
        self.button.clicked.connect(self.new_game)

        self.button = QPushButton('AGAIN', self)
        grid.addWidget(self.button, 2, 0)
        self.button.clicked.connect(self.again)

        self.setLayout(grid)
        self.show()

    def new_game(self):
        self.close()
        self.game = Game(self.name)

    def again(self):
        self.GuiField = Board(self.height, self.width, self.colors, self.name)
        self.GuiField.field.start_game()
        q = QDesktopWidget().availableGeometry()
        self.GuiField.resize(q.width(), q.height())
        self.GuiField.showFullScreen()


class PointPainter(QDialog):
    def __init__(self, score):
        super().__init__()

        q = QDesktopWidget().availableGeometry()
        self.resize(q.width() // 4, q.height() // 8)

        grid = QGridLayout()

        self.lbl = QLabel('SCORE:' + str(score))
        grid.addWidget(self.lbl, 0, 0)

        self.button = QPushButton('OK', self)
        grid.addWidget(self.button, 1, 0)
        self.button.clicked.connect(self.on_click)

        self.setLayout(grid)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def on_click(self):
        self.close()


class PointCounter(QDialog):
    def __init__(self, score, height, width, colors, board):
        super().__init__()
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.max_score = score
        self.logic = Logic()
        self.state = FieldState(height, width, colors)
        self.is_stoppped = False
        self.open = False

        q = QDesktopWidget().availableGeometry()
        self.resize(q.width() // 4, q.height() // 8)

        grid = QGridLayout()

        self.lbl = QLabel('CALCULATING...')
        grid.addWidget(self.lbl, 0, 0)

        self.button = QPushButton('STOP', self)
        grid.addWidget(self.button, 1, 0)
        self.button.clicked.connect(self.on_click)

        self.setLayout(grid)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()
        self.setFocus()

        try:
            p = Thread(target=self.count_possible_score(deepcopy(board), score), daemon=True)
            p.setDaemon(True)
            p.start()
            #p.run()
            #p.join(0.1)

        except Exception:
            pass



    def on_click(self):
        self.is_stoppped = True
        self.close()
        self.painter = PointPainter(self.max_score)
        self.painter.show()


    def count_possible_score(self, new_board, score):
        board = deepcopy(new_board)
        visited = set()
        for i in range(len(board)):
            for j in range(len(board[i])):
                if (j, i) in visited:
                    continue
                if not self.state.no_steps(board):
                    to_delete = self.logic.find_block(board, j, i)
                    for x, y in to_delete:
                        visited.add((x, y))
                    if len(to_delete) >= 2:
                        new_board = deepcopy(board)
                        n = self.state.count_score(len(to_delete))
                        self.logic.shift(new_board, to_delete)
                        self.count_possible_score(new_board, n + score)
        self.max_score = max(self.max_score, score)
        if self.is_stoppped:
            self.max_score = -1
            raise Exception


class Board(QMainWindow):
    COLOR_TABLE = [0xFFFFFF, 0x66CC00, 0x7788BB, 0x9977AA,
                   0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00,
                   0xCC0000, 0x6C00DD, 0x00DDFF]

    def __init__(self, height, width, colors, name = None):
        super().__init__()
        self.name = name
        q = QDesktopWidget().availableGeometry()
        self.cube_side = min(q.height() // (2 + height), q.width() // (3 + width))
        self.field = FieldState(height, width, colors)
        self.setMouseTracking(True)
        self.is_paused = False

        self.undo_btn = QPushButton('UNDO', self)
        self.undo_btn.move(self.cube_side * width, self.cube_side * 4)
        self.undo_btn.resize(self.cube_side * 2, self.cube_side * 2)
        self.undo_btn.clicked.connect(self.undo)

        self.rendo_btn = QPushButton('RENDO', self)
        self.rendo_btn.move(self.cube_side * width, self.cube_side * 2)
        self.rendo_btn.resize(self.cube_side * 2, self.cube_side * 2)
        self.rendo_btn.clicked.connect(self.rendo)

        self.restart_btn = QPushButton('RESTART', self)
        self.restart_btn.move(self.cube_side * (2 + width), 2 * self.cube_side)
        self.restart_btn.resize(self.cube_side * 2, self.cube_side * 2)
        self.restart_btn.clicked.connect(self.restart)

        self.new_game_btn = QPushButton('NEW\nGAME', self)
        self.new_game_btn.move(self.cube_side * (2 + width), 4 * self.cube_side)
        self.new_game_btn.resize(self.cube_side * 2, self.cube_side * 2)
        self.new_game_btn.clicked.connect(self.new_game)

        self.scores_btn = QPushButton('COUNT\nSCORE', self)
        self.scores_btn.move(self.cube_side * width, 6 * self.cube_side)
        self.scores_btn.resize(self.cube_side * 2, self.cube_side * 2)
        self.scores_btn.clicked.connect(self.count_score)

        self.scores = ScoresTable()
        size = "{}*{}".format(self.field.height, self.field.width)

        if self.scores is not None:
            try:
                self.best_score = QLabel(
                    "Best result:\n" + str(self.scores.score_table[size][self.field.colors_number][0]["score"]), self)
                if self.scores.score_table[size][self.field.colors_number][0]["score"] == 0:
                    self.best_score.setText('')
                self.best_score.move(self.cube_side * (2 + width), 0)
                self.best_score.resize(self.cube_side, self.cube_side)
            except:
                self.scores = None
                print("WARNING: Scores file is damaged")

        self.total_score = QLabel('Total:\n' + str(self.field.score), self)
        self.total_score.move(self.cube_side * (1 + width), 0)
        self.total_score.resize(self.cube_side, self.cube_side)
        self.cur_price = QLabel('', self)
        self.cur_price.move(self.cube_side * width, 0)
        self.cur_price.resize(self.cube_side, self.cube_side)

        blocks_number = QLabel('Number of blocks:', self)
        blocks_number.move(0, self.cube_side * self.field.height)
        blocks_number.resize(self.cube_side * 3, self.cube_side)

    def count_score(self):
        if self.is_paused:
            return
        self.is_paused = True
        self.counter = PointCounter(self.field.score,
                                    self.field.height,
                                    self.field.width,
                                    self.field.colors_number,
                                    self.field.board)
        self.is_paused = False


    def new_game(self):
        if self.is_paused:
            return
        self.close()
        self.options = NewGameOptions(self.name, self.field.height, self.field.width, self.field.colors_number)

    def mousePressEvent(self, event):
        if self.is_paused:
            return
        y = self.field.height - 1 - event.pos().y() // self.cube_side
        x = event.pos().x() // self.cube_side
        if y < self.field.height and x < self.field.width:
            to_delete = self.field.logic.find_block(self.field.board, x, y)
            if len(to_delete) >= 2:
                self.field.score += self.field.count_score(len(to_delete))
                self.field.logic.shift(self.field.board, to_delete)
                self.total_score.setText('Total:\n' + str(self.field.score))
                if self.field.no_steps(self.field.board):
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
        for i in range(self.field.height):
            for j in range(self.field.width - 1, -1, -1):
                x = self.contentsRect().left() + j * self.cube_side
                y = (self.field.height - 1 - i) * self.cube_side
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
                painter.fillRect(k[0] * self.cube_side, (self.field.height - 1 - k[1]) * self.cube_side,
                                 self.cube_side - 5,
                                 self.cube_side - 5,
                                 QColor(self.COLOR_TABLE[self.field.board[k[0]][k[1]]]).lighter())
            self.cur_price.setText('Price:\n' + str(self.field.count_score(len(self.field.make_lighter[1]))))
        else:
            self.cur_price.setText('')
        painter.setFont(QFont('Decorative', self.cube_side // 4))
        for i in range(self.field.colors_number):
            painter.setPen(QColor(self.COLOR_TABLE[i + 1]))
            painter.drawText(i * self.cube_side, self.cube_side * (2 + self.field.height),
                             str(self.field.rest_block[i]))

        if not self.field.is_started:
            self.close()
            if self.scores is not None:
                if self.name is None:
                    self.name_request = NameRequest()
                    self.name_request.show()
                    self.name_request.exec_()
                    try:
                        self.name = self.name_request.name
                    except:
                        exit(1)
                    self.name_request.close()

                self.res = ResultPainter(self.name, deepcopy(self.scores), self.field.score, self.field.height, self.field.width, self.field.colors_number)
                self.res.show()

    def mouseMoveEvent(self, event):
        if self.is_paused:
            return
        y = self.field.height - 1 - event.pos().y() // self.cube_side
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
        if self.is_paused:
            return
        self.field.undo()
        self.update()

    def rendo(self):
        if self.is_paused:
            return
        self.field.rendo()
        self.update()

    def restart(self):
        if self.is_paused:
            return
        self.field.is_started = True
        self.field.score = 0
        self.field.make_lighter = (False, [])
        self.field.board = deepcopy(self.field.start_board)
        self.field.previous = []
        self.field.next = []
        self.update()
