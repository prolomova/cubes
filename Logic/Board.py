from copy import deepcopy
from PyQt5.QtWidgets import QDesktopWidget, QPushButton, \
    QDialog, QGridLayout, QLineEdit, QLabel, QMainWindow
from PyQt5.QtGui import QPainter, QColor, QFont, QPalette
from PyQt5.QtCore import QTimer, QCoreApplication
from Logic.Field import FieldState, Logic
from threading import Thread
from PyQt5 import QtWidgets
from Logic.Score import NameRequest, ResultPainter, ScoresTable
from Logic.Options import NewGameOptions


class Board(QMainWindow):
    COLOR_TABLE = [0xFFFFFF, 0x66CC00, 0x7788BB, 0x9977AA,
                   0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00,
                   0xCC0000, 0x6C00DD, 0x00DDFF]

    def __init__(self, height, width, colors, name=None):
        super().__init__()
        self.name = name
        q = QDesktopWidget().availableGeometry()
        self.cube_side = min(q.height() // (3 + height),
                             q.width() // (3 + width))
        self.field = FieldState(height, width, colors)
        self.setMouseTracking(True)
        self.is_paused = False
        self.counter = None
        self.is_changed = False

        self.scores = ScoresTable()
        size = "{}*{}".format(self.field.height, self.field.width)

        if self.scores is not None:
            try:
                score = self.scores \
                    .score_table[size][self.field.colors_number][0]["score"]
                score = str(score)
                self.best_score = QLabel(
                    "Best result:\n" + score, self)
                colors = self.field.colors_number
                if self.scores.score_table[size][colors][0]["score"] == 0:
                    self.best_score.setText('')
                self.best_score.move(self.cube_side * (2 + width), 0)
                self.best_score.resize(self.cube_side, self.cube_side)
            except (KeyError, IOError, TypeError):
                self.scores = None
                self.statusBar().showMessage("WARNING: Scores file is damaged")

        self.total_score = QLabel('Total:\n' + str(self.field.score), self)
        self.total_score.move(self.cube_side * (1 + width), 0)
        self.total_score.resize(self.cube_side, self.cube_side)

        self.possible_score = QLabel('', self)
        self.possible_score.move(self.cube_side * (3 + width), 0)
        self.possible_score.resize(self.cube_side, self.cube_side)

        self.cur_price = QLabel('', self)
        self.cur_price.move(self.cube_side * width, 0)
        self.cur_price.resize(self.cube_side, self.cube_side)

        blocks_number = QLabel('Number of blocks:', self)
        blocks_number.move(0, self.cube_side * self.field.height)
        blocks_number.resize(self.cube_side * 3, self.cube_side)

        self.menu_init()

    def menu_init(self):
        new_game_mn = QtWidgets.QAction('&New Game', self)
        new_game_mn.setShortcut('Ctrl+N')
        new_game_mn.setStatusTip('New Game')
        new_game_mn.triggered.connect(self.new_game)

        restart_mn = QtWidgets.QAction('&Restart', self)
        restart_mn.setShortcut('Ctrl+R')
        restart_mn.setStatusTip('Restart current game')
        restart_mn.triggered.connect(self.restart)

        count_mn = QtWidgets.QAction('&Count score', self)
        count_mn.setShortcut('Ctrl+C')
        count_mn.setStatusTip('Count possible score')
        count_mn.triggered.connect(self.count_score)

        undo_mn = QtWidgets.QAction('&Undo', self)
        undo_mn.setShortcut('Ctrl+Z')
        undo_mn.setStatusTip('Undo')
        undo_mn.triggered.connect(self.undo)

        rendo_mn = QtWidgets.QAction('&Rendo', self)
        rendo_mn.setShortcut('Ctrl+Shift+Z')
        rendo_mn.setStatusTip('Rendo')
        rendo_mn.triggered.connect(self.rendo)

        self.statusBar()
        menubar = self.menuBar()

        options = menubar.addMenu('&Options')
        options.addAction(new_game_mn)
        options.addAction(restart_mn)
        options.addAction(count_mn)

        options = menubar.addMenu('&Edit')
        options.addAction(undo_mn)
        options.addAction(rendo_mn)

    def count_score(self):
        if self.is_paused:
            return

        self.timer = QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start()
        self.is_paused = True

        self.is_changed = False
        self.field.stop_calculating = False
        p = Thread(target=self.field.count_possible_score,
                   args=(deepcopy(self.field.board), self.field.score),
                   daemon=True)
        p.start()

    def new_game(self):
        if self.is_paused:
            return
        self.close()
        self.options = NewGameOptions(self.name,
                                      self.field.height,
                                      self.field.width,
                                      self.field.colors_number)

    def timerEvent(self):
        self.timer.stop()
        self.field.stop_calculating = True
        self.is_paused = False
        self.update()

    def mousePressEvent(self, event):
        if self.is_paused:
            event.ignore()
            self.update()
            return
        y = self.field.height - 1 - event.pos().y() // self.cube_side
        x = event.pos().x() // self.cube_side
        if y < self.field.height and x < self.field.width:
            to_delete = self.field.logic.find_block(self.field.board, x, y)
            if len(to_delete) >= 2:
                self.is_changed = True
                self.field.score += self.field.count_score(len(to_delete))
                self.field.logic.shift(self.field.board, to_delete)
                self.total_score.setText('Total:\n' + str(self.field.score))
                if self.field.no_steps(self.field.board):
                    self.field.is_started = False
            if 0 <= x < len(self.field.board) \
                    and 0 <= y < len(self.field.board[x]):
                to_delete = self.field.logic.find_block(self.field.board, x, y)
                if len(to_delete) < 2:
                    self.field.make_lighter = (False, [])
                else:
                    self.field.make_lighter = (True, to_delete)
            else:
                self.field.make_lighter = (False, [])
            self.field.previous.append((deepcopy(self.field.board),
                                        self.field.score,
                                        self.field.max_score))
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
                if len(self.field.board) > j >= 0 \
                        and 0 <= i < len(self.field.board[j]):
                    color = QColor(self.COLOR_TABLE[self.field.board[j][i]])
                    painter.fillRect(x, y,
                                     self.cube_side - 5,
                                     self.cube_side - 5,
                                     color)
                else:
                    painter.fillRect(x, y,
                                     self.cube_side - 5,
                                     self.cube_side - 5,
                                     QColor(self.COLOR_TABLE[0]))

        if self.field.make_lighter[0]:
            for k in self.field.make_lighter[1]:
                color = QColor(self.COLOR_TABLE[self.field.board[k[0]][k[1]]])\
                    .lighter()
                painter.fillRect(k[0] * self.cube_side,
                                 (self.field.height - 1 - k[1])
                                 * self.cube_side,
                                 self.cube_side - 5,
                                 self.cube_side - 5,
                                 color)
            price = self.field.count_score(len(self.field.make_lighter[1]))
            price = str(price)
            self.cur_price.setText('Price:\n' + price)
        else:
            self.cur_price.setText('')

        painter.setFont(QFont('Decorative', self.cube_side // 4))
        for i in range(self.field.colors_number):
            painter.setPen(QColor(self.COLOR_TABLE[i + 1]))
            painter.drawText(i * self.cube_side,
                             self.cube_side * (2 + self.field.height),
                             str(self.field.rest_block[i]))

        if self.field.max_score != 0 and not self.is_changed:
            self.possible_score.setText(
                "Possible score:\n" + str(self.field.max_score))
        else:
            self.possible_score.setText("")

        if not self.field.is_started:
            self.close()
            if self.scores is not None:
                if self.name is None:
                    self.name_request = NameRequest()
                    self.name_request.show()
                    self.name_request.exec_()
                    try:
                        self.name = self.name_request.name
                    except AttributeError:
                        QCoreApplication.exit()
                        return
                    self.name_request.close()

                self.res = ResultPainter(self.name,
                                         deepcopy(self.scores),
                                         self.field.score,
                                         self.field.height,
                                         self.field.width,
                                         self.field.colors_number)
                self.res.show()

    def mouseMoveEvent(self, event):
        if self.is_paused:
            event.ignore()
            self.update()
            return
        y = self.field.height - 1 - event.pos().y() // self.cube_side
        x = event.pos().x() // self.cube_side
        if 0 <= x < len(self.field.board) \
                and 0 <= y < len(self.field.board[x]):
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
