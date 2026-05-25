import sys
import random
import numpy as np
import pygame
from collections import deque
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup, QDialog, QMessageBox
)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt

# ------------------------ calculate.py ------------------------
class Calculate:
    def __init__(self, maze):
        self.maze = maze
        self.shortest_path = self.calculate_shortest_path()
        print("Shortest Path:", self.shortest_path)
        
    def return_shortest_path(self):
        return self.shortest_path

    def calculate_shortest_path(self):
        maze = self.maze
        start_position = (0, 1)
        end_position = (len(maze) - 2, len(maze[0]) - 2)

        visited = [[False] * len(maze[0]) for _ in range(len(maze))]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = deque([(start_position, 0)])
        visited[start_position[0]][start_position[1]] = True

        while queue:
            position, distance = queue.popleft()

            if position == end_position:
                return distance

            for direction in directions:
                next_position = (position[0] + direction[0], position[1] + direction[1])

                if (
                    0 <= next_position[0] < len(maze)
                    and 0 <= next_position[1] < len(maze[0])
                    and maze[next_position[0]][next_position[1]] == 0
                    and not visited[next_position[0]][next_position[1]]
                ):
                    queue.append((next_position, distance + 1))
                    visited[next_position[0]][next_position[1]] = True

        return -1

# ------------------------ env.py ------------------------
class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        random.shuffle(self.dir)

    def get_cur_pos(self):
        return self.x, self.y

    def get_next_pos(self):
        if self.dir:
            return self.dir.pop()
        else:
            return None

def make_maze(size):
    rooms = [[Room(x, y) for x in range(size)] for y in range(size)]
    maze = [[1 for _ in range(size * 2 + 1)] for _ in range(size * 2 + 1)]

    visited = []

    def make(cur_room):
        cx, cy = cur_room.get_cur_pos()
        visited.append((cx, cy))
        maze[cy * 2 + 1][cx * 2 + 1] = 0
        while cur_room.dir:
            next_pos = cur_room.get_next_pos()
            if next_pos:
                nx, ny = next_pos
                if 0 <= nx < size and 0 <= ny < size:
                    if (nx, ny) not in visited:
                        # Remove wall between current room and next room
                        wall_x = cx + nx + 1
                        wall_y = cy + ny + 1
                        maze[wall_y][wall_x] = 0
                        make(rooms[ny][nx])

    make(rooms[0][0])

    return maze

# ------------------------ make_env.py ------------------------
class MazeBuilder(QDialog):
    def __init__(self, maze_size, parent=None):
        super().__init__(parent)
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
        self.setFixedSize(600, 650)  # Height includes space for the Save button

        self.save_button = QPushButton("Save Maze", self)
        self.save_button.clicked.connect(self.accept)
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
            elif self.maze[row][col] == 2 or self.maze[row][col] == 3:
                # Prevent toggling start and exit positions
                return
            self.update()

    def get_maze(self):
        # Ensure start and exit are correctly set
        self.maze[1][1] = 3  # Start position
        self.maze[self.maze_size - 2][self.maze_size - 1] = 2  # Exit position
        return self.maze

def create_custom_maze(maze_size, parent=None):
    dialog = MazeBuilder(maze_size, parent)
    if dialog.exec_() == QDialog.Accepted:
        return np.array(dialog.get_maze())
    else:
        return None

def make_random_maze(maze_size):
    return np.array(make_maze(maze_size))

# ------------------------ maze_ai.py ------------------------
class Maze_ai:
    def __init__(self, maze, visualize, episodes, viz_divisor):
        self.maze = maze
        self.visualize = visualize
        self.ep_num = episodes
        self.viz_divisor = viz_divisor

        self.maze_height = len(self.maze)
        self.maze_width = len(self.maze[0])
        self.maze[self.maze_height - 2][self.maze_width - 1] = 2  # Exit position

        self.actions = ['up', 'down', 'left', 'right']
        self.q_table = np.zeros((self.maze_height, self.maze_width, len(self.actions)))

        # Hyperparameters
        self.learning_rate = 0.1
        self.discount_factor = 0.99
        self.exploration_rate = 1.0  # Initial exploration rate
        self.exploration_decay = 0.995
        self.min_exploration_rate = 0.01

        # Calculate shortest path
        self.shortest_path = Calculate(self.maze).return_shortest_path() + 1
        print(f"Shortest Path: {self.shortest_path}")

        # Calculate visualization interval
        self.visualization_interval = max(1, (self.ep_num // self.viz_divisor))

        # Run simulation
        self.run_simulation()

    def run_simulation(self):
        pygame.init()
        if self.visualize:
            screen_width, screen_height = 800, 800
            screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Maze Solver")

            WHITE = (255, 255, 255)
            BLACK = (0, 0, 0)
            GREEN = (0, 255, 0)
            BLUE = (0, 0, 255)
            RED = (255, 0, 0)

            cell_width = screen_width // self.maze_width
            cell_height = screen_height // self.maze_height
            cell_size = min(cell_width, cell_height)

            clock = pygame.time.Clock()

        agent_position = (1, 1)
        current_episode = 1
        fail_count = 0
        move_count = 0
        total_reward = 0

        while current_episode <= self.ep_num:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Exploration or exploitation
            if random.uniform(0, 1) < self.exploration_rate:
                action_index = random.randint(0, len(self.actions) - 1)  # Explore
            else:
                action_index = np.argmax(self.q_table[agent_position])  # Exploit

            action = self.actions[action_index]

            # Agent's movement
            next_position = agent_position
            if action == 'up' and agent_position[0] > 0:
                next_position = (agent_position[0] - 1, agent_position[1])
            elif action == 'down' and agent_position[0] < self.maze_height - 1:
                next_position = (agent_position[0] + 1, agent_position[1])
            elif action == 'left' and agent_position[1] > 0:
                next_position = (agent_position[0], agent_position[1] - 1)
            elif action == 'right' and agent_position[1] < self.maze_width - 1:
                next_position = (agent_position[0], agent_position[1] + 1)

            # Reward and penalties
            if self.maze[next_position[0]][next_position[1]] == 1:  # Wall
                reward = -100
                fail_count += 1
                next_position = agent_position  # Prevent movement
            elif self.maze[next_position[0]][next_position[1]] == 2:  # Goal
                reward = 100
                if current_episode % self.visualization_interval == 0:
                    print(f"Episode {current_episode} completed")
                current_episode += 1
                agent_position = (1, 1)
                fail_count = 0
                move_count = 0
                total_reward = 0
                self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)
                continue
            else:  # Normal move
                reward = -1

            # Update Q-Table
            self.q_table[agent_position][action_index] += self.learning_rate * (
                reward
                + self.discount_factor * np.max(self.q_table[next_position])
                - self.q_table[agent_position][action_index]
            )

            # Move agent
            agent_position = next_position
            move_count += 1
            total_reward += reward

            # Visualization based on user-defined interval
            if self.visualize and current_episode % self.visualization_interval == 0:
                screen.fill(WHITE)
                for row in range(self.maze_height):
                    for col in range(self.maze_width):
                        x = col * cell_size
                        y = row * cell_size
                        if self.maze[row][col] == 1:
                            pygame.draw.rect(screen, BLACK, (x, y, cell_size, cell_size))
                        elif self.maze[row][col] == 2:
                            pygame.draw.rect(screen, GREEN, (x, y, cell_size, cell_size))
                pygame.draw.rect(screen, BLUE, (agent_position[1] * cell_size, agent_position[0] * cell_size, cell_size, cell_size))

                # Display episode, reward, fail count, move count, and shortest path
                font = pygame.font.SysFont('Arial', 24)
                episode_text = font.render(f"Episode: {current_episode}", True, RED)
                reward_text = font.render(f"Reward: {total_reward}", True, RED)
                fail_text = font.render(f"Fails: {fail_count}", True, RED)
                move_text = font.render(f"Moves: {move_count}", True, RED)
                shortest_path_text = font.render(f"Shortest Path: {self.shortest_path}", True, RED)
                
                # Render the text in the desired order
                screen.blit(episode_text, (10, 10))
                screen.blit(reward_text, (10, 40))
                screen.blit(fail_text, (10, 70))
                screen.blit(move_text, (10, 100))
                screen.blit(shortest_path_text, (10, 130))

                pygame.display.flip()
                clock.tick(10)

        if self.visualize:
            pygame.quit()

# ------------------------ simulation.py ------------------------
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
        self.maze_size_input.setPlaceholderText("Enter maze size (e.g., 10)")

        # Number of episodes input
        self.episode_label = QLabel("Number of Episodes:")
        self.episode_input = QLineEdit(self)
        self.episode_input.setPlaceholderText("Enter number of episodes (e.g., 1000)")

        # Visualization frequency input
        self.viz_divisor_label = QLabel("Visualization Frequency Divisor:")
        self.viz_divisor_input = QLineEdit(self)
        self.viz_divisor_input.setPlaceholderText("Enter divisor (e.g., 5)")
        self.viz_divisor_input.setText("5")  # Set default value to 5

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
        layout.addWidget(self.viz_divisor_label)
        layout.addWidget(self.viz_divisor_input)
        layout.addWidget(self.maze_type_label)
        layout.addWidget(self.random_maze_radio)
        layout.addWidget(self.create_maze_radio)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def run_simulation(self):
        # Fetch user inputs
        maze_size = self.maze_size_input.text()
        episodes = self.episode_input.text()
        viz_divisor = self.viz_divisor_input.text()

        # Determine maze type
        if self.random_maze_radio.isChecked():
            maze_type = "random"
        elif self.create_maze_radio.isChecked():
            maze_type = "create"
        else:
            self.show_error("Please select a maze type.")
            return

        # Validate inputs
        if not maze_size.isdigit() or not episodes.isdigit() or not viz_divisor.isdigit():
            self.show_error("Please enter valid numeric values for maze size, number of episodes, and visualization frequency divisor.")
            return

        # Convert inputs to correct types
        maze_size = int(maze_size)
        episodes = int(episodes)
        viz_divisor = int(viz_divisor)
        if viz_divisor <= 0:
            self.show_error("Visualization frequency divisor must be a positive integer.")
            return

        # Initialize maze based on type
        if maze_type == "random":
            maze = make_random_maze(maze_size)
        elif maze_type == "create":
            maze = create_custom_maze(maze_size, self)
            if maze is None:
                # User canceled maze creation
                return
        else:
            self.show_error("Invalid maze type selected.")
            return

        # Run Maze_ai
        try:
            # Close the current UI
            self.close()
            # Instantiate and run Maze_ai
            Maze_ai(maze=maze, visualize=True, episodes=episodes, viz_divisor=viz_divisor)
        except Exception as e:
            self.show_error(f"Error running simulation: {e}")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

# ------------------------ Main Execution ------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulationApp()
    window.resize(400, 400)
    window.show()
    sys.exit(app.exec_())
