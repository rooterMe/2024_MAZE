import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup
)
import subprocess


class SimulationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Maze AI Simulation")

        layout = QVBoxLayout()

        # Maze size input
        self.maze_size_label = QLabel("Maze Size:")
        self.maze_size_input = QLineEdit(self)
        self.maze_size_input.setPlaceholderText("Enter maze size")

        # Number of episodes input
        self.episode_label = QLabel("Number of Episodes:")
        self.episode_input = QLineEdit(self)
        self.episode_input.setPlaceholderText("Enter episodes")

        # Maze type selection (Random or Create)
        self.maze_type_label = QLabel("Maze Type:")
        self.random_maze_radio = QRadioButton("Random Maze")
        self.create_maze_radio = QRadioButton("Create Maze")
        self.random_maze_radio.setChecked(True)  # Default selection

        self.maze_type_group = QButtonGroup()
        self.maze_type_group.addButton(self.random_maze_radio)
        self.maze_type_group.addButton(self.create_maze_radio)

        # Run button
        self.run_button = QPushButton("Run Simulation")
        self.run_button.clicked.connect(self.run_simulation)

        # Layout organization
        layout.addWidget(self.maze_size_label)
        layout.addWidget(self.maze_size_input)
        layout.addWidget(self.episode_label)
        layout.addWidget(self.episode_input)
        layout.addWidget(self.maze_type_label)
        layout.addWidget(self.random_maze_radio)
        layout.addWidget(self.create_maze_radio)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def run_simulation(self):
        # Fetch user inputs
        maze_size = self.maze_size_input.text()
        episodes = self.episode_input.text()

        # Determine maze type
        if self.random_maze_radio.isChecked():
            maze_type = "random"
        elif self.create_maze_radio.isChecked():
            maze_type = "create"
        else:
            self.show_error("Please select a maze type.")
            return

        # Validate inputs
        if not maze_size.isdigit() or not episodes.isdigit():
            self.show_error("Please enter valid numeric values for maze size and number of episodes.")
            return

        # Build command
        command = [
            "python", "maze_ai.py",
            f"--maze_size", maze_size,
            f"--episode", episodes,
            f"--maze", maze_type  # Add maze type to the command
        ]

        try:
            # Close the current UI
            self.close()
            # Execute the command
            subprocess.run(command, check=True)
            print(command)
        except Exception as e:
            self.show_error(f"Error running simulation: {e}")

    def show_error(self, message):
        error_dialog = QLabel(f"Error: {message}")
        error_dialog.setStyleSheet("color: red;")
        error_layout = QVBoxLayout()
        error_layout.addWidget(error_dialog)
        error_window = QWidget()
        error_window.setWindowTitle("Error")
        error_window.setLayout(error_layout)
        error_window.resize(300, 100)
        error_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulationApp()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())
