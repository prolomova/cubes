from PyQt5.QtWidgets import QDesktopWidget, QPushButton, \
    QDialog, QGridLayout
from cubes import Game
from Logic import Board


class NewGameOptions(QDialog):
    def __init__(self, name, height=None, width=None, colors=None):
        super().__init__()
        self.height = height
        self.width = width
        self.colors = colors
        self.name = name
        q = QDesktopWidget().availableGeometry()
        self.setFixedSize(q.width() // 4, q.height() // 8)

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
        self.GuiField = Board.Board(self.height,
                                    self.width,
                                    self.colors,
                                    self.name)
        self.GuiField.field.start_game()
        q = QDesktopWidget().availableGeometry()
        self.GuiField.move(0, 0)
        self.GuiField.setFixedSize(q.width(), q.height())
        self.GuiField.showFullScreen()
