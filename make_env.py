import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt
import env


class MazeBuilder(QWidget):
    def __init__(self, maze_size):
        super().__init__()
        self.maze_size = maze_size + 2  # Include the border
        self.cell_size = 600 // self.maze_size
        self.maze = [[1 for _ in range(self.maze_size)] for _ in range(self.maze_size)]

        # Initialize inner paths to 0
        for row in range(1, self.maze_size - 1):
            for col in range(1, self.maze_size - 1):
                self.maze[row][col] = 0

        # Ensure start and exit positions
        self.maze[1][1] = 3  # Start position
        self.maze[self.maze_size - 2][self.maze_size - 1] = 2  # Exit position

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Create Maze")
        self.resize(600, 650)  # Height includes space for the Save button
        self.save_button = QPushButton("Save Maze", self)
        self.save_button.clicked.connect(self.close)
        self.save_button.setGeometry(250, 10, 100, 40)

    def paintEvent(self, event):
        painter = QPainter(self)
        for row in range(self.maze_size):
            for col in range(self.maze_size):
                x = col * self.cell_size
                y = row * self.cell_size + 50
                if self.maze[row][col] == 1:  # Wall
                    painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(0, 0, 0))
                elif self.maze[row][col] == 2:  # Exit
                    painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(0, 255, 0))
                elif self.maze[row][col] == 3:  # Start
                    painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(0, 0, 255))
                elif self.maze[row][col] == 0:  # Path
                    painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(255, 255, 255))
                painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
                painter.drawRect(x, y, self.cell_size, self.cell_size)

    def mousePressEvent(self, event):
        if event.y() < 50:  # Ignore clicks on the Save button area
            return

        col = event.x() // self.cell_size
        row = (event.y() - 50) // self.cell_size

        # Ensure clicks are inside the editable area
        if 1 <= row < self.maze_size - 1 and 1 <= col < self.maze_size - 1:
            if self.maze[row][col] == 0:
                self.maze[row][col] = 1  # Wall
            elif self.maze[row][col] == 1:
                self.maze[row][col] = 0  # Path
            self.update()

    def get_maze(self):
        # Ensure start and exit are correctly set
        self.maze[1][1] = 3  # Start position
        self.maze[self.maze_size - 2][self.maze_size - 1] = 2  # Exit position
        return self.maze


def create_custom_maze(maze_size):
    app = QApplication([])
    builder = MazeBuilder(maze_size)
    builder.show()
    app.exec_()
    return np.array(builder.get_maze())


def make_random_maze(maze_size):
    return np.array(env.make_maze(maze_size))
