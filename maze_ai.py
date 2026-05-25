import pygame
import numpy as np
import argparse
import calculate
from make_env import create_custom_maze, make_random_maze


class Maze_ai():
    def __init__(self, maze_size, visualize, episodes, maze_type):
        self.maze_size = maze_size
        self.visualize = visualize
        self.ep_num = episodes
        self.maze_type = maze_type

        # Maze initialization
        if maze_type == "random":
            self.maze = make_random_maze(maze_size)
        elif maze_type == "create":
            self.maze = create_custom_maze(maze_size)
        else:
            raise ValueError("Invalid maze type. Choose 'random' or 'create'.")

        self.maze_height = len(self.maze)
        self.maze_width = len(self.maze[0])
        self.maze[self.maze_height - 2][self.maze_width - 1] = 2  # Exit 위치 설정

        self.actions = ['up', 'down', 'left', 'right']
        self.q_table = np.zeros((self.maze_height, self.maze_width, len(self.actions)))

        # Hyperparameters
        self.learning_rate = 0.1
        self.discount_factor = 0.99
        self.exploration_rate = 1.0  # Initial exploration rate
        self.exploration_decay = 0.995
        self.min_exploration_rate = 0.01

        # Calculate shortest path
        self.shortest_path = calculate.Calculate(self.maze).return_shortest_path() + 1
        print(f"Shortest Path: {self.shortest_path}")

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
            # Exploration or exploitation
            if np.random.uniform(0, 1) < self.exploration_rate:
                action_index = np.random.randint(len(self.actions))  # Explore
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
                if current_episode % (self.ep_num // 10) == 0:
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

            # Visualization only every 10% of episodes
            if self.visualize and current_episode % (self.ep_num // 10) == 0:
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--maze_size', type=int, default=10)
    parser.add_argument('--visualize', type=bool, default=True)
    parser.add_argument('--episode', type=int, default=1000)
    parser.add_argument('--maze', type=str, default="random", help="Choose 'random' or 'create'")
    args = parser.parse_args()

    Maze_ai(args.maze_size, args.visualize, args.episode, args.maze)
