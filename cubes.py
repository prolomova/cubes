import PyQt5
import sys
from Logic import Board
from PyQt5.QtWidgets import QDialog, \
    QGridLayout, QLabel, QSpinBox, QPushButton, \
    QDesktopWidget, QMainWindow, QComboBox


class Game(QDialog):
    def __init__(self, name=None):
        super().__init__()
        self.name = name
        q = QDesktopWidget().availableGeometry()
        self.setFixedSize(q.width() // 4, q.height() // 4)
        self.tbl_size = 2
        self.min_colors = 2
        self.max_colors = 6

        self.grid = QGridLayout()

        self.size_lbl = QLabel()
        self.size_lbl.setText("Выберете размер поля")
        self.grid.addWidget(self.size_lbl, 0, 0)

        self.combo = QComboBox(self)
        self.combo.addItem("6x6")
        self.combo.addItem("12x12")
        self.combo.addItem("15x15")
        self.combo.addItem("25x25")
        self.grid.addWidget(self.combo, 1, 0)
        self.combo.activated[str].connect(self.on_activated)

        self.setLayout(self.grid)

        self.show()

    def on_activated(self, text):
        self.height, self.width = [int(i) for i in text.split('x')]
        min_colors = 2
        max_colors = 6
        if self.height == 25:
            min_colors = 4
            max_colors = 10

        self.colors_lbl = QLabel()
        self.colors_lbl.setText("Выберете количество цветов")
        self.grid.addWidget(self.colors_lbl, 2, 0)

        self.color_number = QComboBox(self)
        self.colors_box = QSpinBox(self)
        self.grid.addWidget(self.colors_box, 3, 0)
        self.colors_box.setMinimum(min_colors)
        self.colors_box.setMaximum(max_colors)
        self.button = QPushButton('OK', self)
        self.grid.addWidget(self.button, 4, 0)
        self.button.clicked.connect(self.on_click)
        self.show()

    def on_click(self):
        self.colors = self.colors_box.value()

        self.close()

        self.game = GameForm(self.height, self.width, self.colors, self.name)
        q = QDesktopWidget().availableGeometry()

        self.game.setGeometry(0, 0, q.width(), q.height())

        self.move(0, 0)
        q = QDesktopWidget().availableGeometry()
        self.game.setFixedSize(q.width(), q.height())
        self.game.GuiField.field.start_game()


class GameForm(QMainWindow):

    def __init__(self, height, width, colors, name=None):
        super().__init__()
        self.GuiField = Board.Board(height, width, colors, name)
        q = QDesktopWidget().availableGeometry()
        self.GuiField.setFixedSize(q.width(), q.height())
        self.GuiField.move(0, 0)
        self.GuiField.show()


def main():
    a = PyQt5.QtWidgets.QApplication([])
    game = GameForm(6, 6, 2)
    game.GuiField.field.start_game()
    sys.exit(a.exec_())


if __name__ == '__main__':
    main()
