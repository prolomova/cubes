from PyQt5 import QtCore
from copy import deepcopy
from PyQt5.QtWidgets import QDesktopWidget, QPushButton, \
    QDialog, QGridLayout, QLineEdit, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont
import yaml
from cubes import Game


class NameRequest(QDialog):

    def __init__(self):
        super().__init__()

        q = QDesktopWidget().availableGeometry()
        self.setFixedSize(q.width() // 4, q.height() // 8)

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
    def __init__(self, name, score_table, score,
                 height, width, number_of_colors):
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
        self.setFixedSize(q.width() // 2, q.height() // 2)
        ScoresTable().add(self.name, self.score, self.height,
                          self.width, self.number_of_colors)

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
            score = self.score_table \
                .score_table[size][self.number_of_colors][i]["score"]
            if score <= self.score and first:
                results.append((self.name, self.score))
                first = False
            name = self.score_table \
                .score_table[size][self.number_of_colors][i]["name"]
            results.append((name, score))
        if first:
            results.append((self.name, self.score))
        main_label = QLabel("SCORE TABLE", self)
        self.grid.addWidget(main_label, 0, 0)
        main_label.setFont(QFont("Times", 18, QFont.Bold))
        i = 1
        first = True
        for name, score in results:
            if name == "":
                break
            label_name = QLabel(name, self)
            label_score = QLabel(str(score), self)
            label_name.setFont(QFont("Times", 15))
            label_score.setFont(QFont("Times", 15))
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
    SCORE_TABLE_FILE_NAME = './Data/scoreTable.yaml'
    TABLE_SIZE = 8

    def __init__(self):
        self.score_table = {}
        try:
            with open(self.SCORE_TABLE_FILE_NAME) as f:
                self.score_table = yaml.load(f)
        except IOError:
            sizes = {'6*6': range(2, 7), '30*30': range(4, 11),
                     '15*15': range(2, 7), '12*12': range(2, 7)}
            for key, value in sizes.items():
                self.score_table[key] = {}
                for colors in value:
                    self.score_table[key][colors] = []
                    for _ in range(8):
                        line = {'name': '', 'score': 0}
                        self.score_table[key][colors].append(line)
            with open(self.SCORE_TABLE_FILE_NAME, 'w') as f:
                yaml.dump(self.score_table, f)

    def add(self, name, score, height, width, number_of_colors):
        size = "{}*{}".format(height, width)
        score_tbl = deepcopy(self.score_table)
        for i in range(self.TABLE_SIZE):
            if score_tbl[size][number_of_colors][i]["score"] <= score:
                score_tbl[size][number_of_colors] \
                    .insert(i, {"name": name, "score": score})
                score_tbl[size][number_of_colors] = \
                    score_tbl[size][number_of_colors][:8]
                break
        with open(self.SCORE_TABLE_FILE_NAME, 'w') as f:
            yaml.dump(score_tbl, f)
