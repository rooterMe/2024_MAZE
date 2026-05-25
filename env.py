import random


class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        random.shuffle(self.dir)

    def get_cur_pos(self):
        return self.x, self.y

    def get_next_pos(self):
        return self.dir.pop()


def make_maze(size):
    rooms = [[Room(x, y) for x in range(size)] for y in range(size)]
    maze = [[1 for _ in range(size * 2 + 1)] for _ in range(size * 2 + 1)]

    visited = []

    def make(cur_room):
        cx, cy = cur_room.get_cur_pos()
        visited.append((cx, cy))
        maze[cy * 2 + 1][cx * 2 + 1] = 0
        while cur_room.dir:
            nx, ny = cur_room.get_next_pos()
            if 0 <= nx < size and 0 <= ny < size:
                if (nx, ny) not in visited:
                    maze[cy + ny + 1][cx + nx + 1] = 0
                    make(rooms[ny][nx])

    make(rooms[0][0])

    return maze