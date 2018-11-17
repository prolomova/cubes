import PyQt5
import sys
import Board
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QSpinBox, QPushButton, QDesktopWidget, QMainWindow

class GameOptions(QDialog):

    def __init__(self, tbl_size, min_colors, max_colors):
        super().__init__()
        self.tbl_size = tbl_size

        grid = QGridLayout()

        q = QDesktopWidget().availableGeometry()
        self.resize(q.width() // 4, q.height() // 8)

        self.lbl_colors = QLabel("Введите количество цветов", self)
        grid.addWidget(self.lbl_colors, 1, 0)
        self.colors_box = QSpinBox(self)
        grid.addWidget(self.colors_box, 2, 0)
        self.colors_box.setMinimum(min_colors)
        self.colors_box.setMaximum(max_colors)
        self.button = QPushButton('OK', self)
        grid.addWidget(self.button, 3, 0)
        self.button.clicked.connect(self.on_click)
        self.setLayout(grid)
        self.show()


    def on_click(self):
        self.colors = self.colors_box.value()

        self.close()

        self.game = GameForm(self.tbl_size, self.colors)
        q = QDesktopWidget().availableGeometry()

        self.game.setGeometry(0, 0, q.width(), q.height())

        self.move(0, 0)
        q = QDesktopWidget().availableGeometry()
        self.game.resize(q.width(), q.height())
        self.game.GuiField.field.start_game()


class Game(QDialog):
    def __init__(self):
        super().__init__()
        q = QDesktopWidget().availableGeometry()
        self.resize(q.width() // 4, q.height() // 4)
        self.tbl_size = 2
        self.min_colors = 2
        self.max_colors = 6

        grid = QGridLayout()

        self.button1 = QPushButton('Размер поля 3х3', self)
        grid.addWidget(self.button1, 1, 0)
        self.button1.clicked.connect(self.on_click1)
        self.button2 = QPushButton('Размер поля 5х5', self)
        grid.addWidget(self.button2, 2, 0)
        self.button2.clicked.connect(self.on_click2)
        self.button3 = QPushButton('Размер поля 6х6', self)
        grid.addWidget(self.button3, 3, 0)
        self.button3.clicked.connect(self.on_click3)
        self.button4 = QPushButton('Размер поля 10х10', self)
        grid.addWidget(self.button4, 4, 0)
        self.button4.clicked.connect(self.on_click4)


        self.setLayout(grid)
        self.show()

    def on_click1(self):
        self.tbl_size = 3
        self.on_click()

    def on_click2(self):
        self.tbl_size = 5
        self.on_click()

    def on_click3(self):
        self.tbl_size = 6
        self.on_click()

    def on_click4(self):
        self.tbl_size = 10
        self.min_colors = 4
        self.max_colors = 10
        self.on_click()

    def on_click(self):
        self.close()
        self.game_options = GameOptions(self.tbl_size, self.min_colors, self.max_colors)


class GameForm(QMainWindow):

    def __init__(self, tbl_size, colors):
        super().__init__()
        self.GuiField = Board.Board(tbl_size, colors)
        q = QDesktopWidget().availableGeometry()
        self.GuiField.resize(q.width(), q.height())
        self.GuiField.showFullScreen()


def main():
    a = PyQt5.QtWidgets.QApplication([])
    game = GameForm(6, 5)
    game.GuiField.field.start_game()
    sys.exit(a.exec_())


if __name__ == '__main__':
    main()
