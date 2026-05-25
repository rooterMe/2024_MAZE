import tkinter as tk
from tkinter import messagebox
from random import randint
from collections import deque

# 전역 변수
map_width = 20
map_height = 15
cell_size = 30
exit_positions = set()
walls = set([(x, 0) for x in range(map_width)] + 
           [(x, map_height - 1) for x in range(map_width)] + 
           [(0, y) for y in range(map_height)] + 
           [(map_width - 1, y) for y in range(map_height)])
fire_positions = set()
people = []
num_people = 5
escaped_people = 0
dead_people = 0
fire_intensity = {}  # 불의 강도 저장 (255에서 3%씩 감소)
fire_spread_queue = deque()  # BFS를 위한 큐
simulation_running = False

# Tkinter 설정 창 및 맵 시각화
def setup_ui():
    def add_exit(x, y):
        if (x, y) in exit_positions:
            exit_positions.remove((x, y))  # 클릭 시 탈출구 삭제
        else:
            if (x, y) not in walls and (x, y) not in fire_positions:
                exit_positions.add((x, y))
        update_label()

    def add_wall(x, y):
        if (x, y) in walls:
            walls.remove((x, y))  # 클릭 시 벽 삭제
        else:
            if (x, y) not in exit_positions and (x, y) not in fire_positions:
                walls.add((x, y))
        update_label()

    def add_fire(x, y):
        if (x, y) in fire_positions:
            fire_positions.remove((x, y))  # 클릭 시 불 삭제
            fire_intensity.pop((x, y), None)
        else:
            if (x, y) not in exit_positions and (x, y) not in walls:
                fire_positions.add((x, y))
                fire_intensity[(x, y)] = 255  # 초기 불의 강도 설정
                fire_spread_queue.append((x, y))  # BFS를 위한 큐에 추가
        update_label()

    def update_label():
        exits_label.config(text=f"Number of Exits: {len(exit_positions)}")
        walls_label.config(text=f"Number of Walls: {len(walls)}")
        fire_label.config(text=f"Number of Fire Spots: {len(fire_positions)}")
        people_status_label.config(text=f"Total People: {num_people}, Escaped: {escaped_people}, Dead: {dead_people}, Alive: {len(people)}")

    def start_simulation():
        global simulation_running
        if simulation_running:  # 이미 시뮬레이션이 진행 중이면 무시
            return
        simulation_running = True  # 시뮬레이션 시작
        global num_people
        try:
            num_people = int(people_count.get())
            if num_people < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("입력 오류", "사람 수는 양의 정수여야 합니다.")
            return
        initialize_people()
        update_label()  # Update labels before starting the simulation
        run_simulation()

    def draw_initial_map():
        canvas.delete("all")
        for x in range(map_width):
            for y in range(map_height):
                canvas.create_rectangle(x * cell_size, y * cell_size, 
                                        (x + 1) * cell_size, (y + 1) * cell_size, 
                                        outline="black", fill="white")
        for (x, y) in exit_positions:
            canvas.create_rectangle(x * cell_size, y * cell_size, 
                                    (x + 1) * cell_size, (y + 1) * cell_size, 
                                    fill="green")
        for (x, y) in walls:
            canvas.create_rectangle(x * cell_size, y * cell_size, 
                                    (x + 1) * cell_size, (y + 1) * cell_size, 
                                    fill="black")
        for (x, y) in fire_positions:
            intensity = fire_intensity.get((x, y), 255)
            intensity = max(0, intensity)  # 색상이 0 이하로 내려가지 않도록 제한
            color = f"#{int(intensity):02x}0000"
            canvas.create_rectangle(x * cell_size, y * cell_size, 
                                    (x + 1) * cell_size, (y + 1) * cell_size, 
                                    fill=color)
        for (x, y) in people:
            canvas.create_oval(x * cell_size + cell_size // 4, y * cell_size + cell_size // 4,
                              (x + 1) * cell_size - cell_size // 4, (y + 1) * cell_size - cell_size // 4,
                              fill="blue")

    def on_canvas_click(event):
        if simulation_running:  # 시뮬레이션이 진행 중이면 클릭을 무시
            return
        x, y = event.x // cell_size, event.y // cell_size
        if 0 <= x < map_width and 0 <= y < map_height:
            if add_mode.get() == "exit":
                add_exit(x, y)
            elif add_mode.get() == "wall":
                add_wall(x, y)
            elif add_mode.get() == "fire":
                add_fire(x, y)
            draw_initial_map()

    def initialize_people():
        global people, escaped_people, dead_people
        people = []
        escaped_people = 0
        dead_people = 0
        attempts = 0
        max_attempts = num_people * 10  # 무한 루프 방지를 위한 시도 횟수 제한
        while len(people) < num_people and attempts < max_attempts:
            x, y = randint(0, map_width - 1), randint(0, map_height - 1)
            if (x, y) not in walls and (x, y) not in exit_positions and (x, y) not in fire_positions and (x, y) not in people:
                people.append((x, y))
            attempts += 1
        if len(people) < num_people:
            messagebox.showwarning("경고", f"사람을 모두 배치하지 못했습니다. 배치된 사람 수: {len(people)}")

    def run_simulation():
        def move_people():
            global escaped_people, dead_people  # Changed from nonlocal to global
            new_people = []
            for i in range(len(people)):
                if people[i] in exit_positions:
                    escaped_people += 1
                    continue  # 이미 탈출한 사람은 제거
                x, y = people[i]
                direction = randint(0, 3)
                if direction == 0:  # Move up
                    dx, dy = 0, -1
                elif direction == 1:  # Move down
                    dx, dy = 0, 1
                elif direction == 2:  # Move left
                    dx, dy = -1, 0
                elif direction == 3:  # Move right
                    dx, dy = 1, 0
                nx, ny = x + dx, y + dy
                if 0 <= nx < map_width and 0 <= ny < map_height and (nx, ny) not in walls:
                    if (nx, ny) in fire_positions:
                        dead_people += 1
                    else:
                        new_people.append((nx, ny))
                else:
                    new_people.append((x, y))  # 이동할 수 없으면 현재 위치 유지
            people[:] = new_people
            update_people_status()
            draw_initial_map()
            if len(people) > 0:
                root.after(200, move_people)

        def spread_fire():
            new_fire_positions = []
            for _ in range(len(fire_spread_queue)):
                (x, y) = fire_spread_queue.popleft()
                intensity = fire_intensity.get((x, y), 255)
                if intensity > 7:  # 최소 밝기 제한
                    fire_intensity[(x, y)] = max(0, int(intensity * 0.97))  # 강도 감소, 0 이하로 내려가지 않도록 제한

                # 상하좌우로 불 퍼짐 (BFS 사용)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in walls or (nx, ny) in fire_positions or (nx, ny) in exit_positions:
                        continue
                    if 0 <= nx < map_width and 0 <= ny < map_height:
                        fire_positions.add((nx, ny))
                        fire_intensity[(nx, ny)] = 255  # 새로 퍼진 불은 최대 강도로 시작
                        fire_spread_queue.append((nx, ny))
            draw_initial_map()
            # 다음 불 확산을 예약 (예: 3000ms = 3초)
            root.after(5000, spread_fire)  # 불 확산 속도를 느리게 설정

        move_people()
        spread_fire()

    def update_people_status():
        people_status_label.config(text=f"Total People: {num_people}, Escaped: {escaped_people}, Dead: {dead_people}, Alive: {len(people)}")

    global root, people_status_label, canvas
    root = tk.Tk()
    root.title("Disaster Escape Simulation Setup")

    # 창 크기 확장
    root.geometry(f"{map_width * cell_size + 500}x{map_height * cell_size + 100}")

    # 사람 수 설정
    tk.Label(root, text="Number of People:").grid(row=0, column=0, padx=5, pady=5)
    people_count = tk.Entry(root)
    people_count.insert(0, "5")
    people_count.grid(row=0, column=1)

    # 추가 모드 설정
    add_mode = tk.StringVar(value="exit")
    tk.Radiobutton(root, text="Add/Remove Exit", variable=add_mode, value="exit").grid(row=1, column=0, padx=5, pady=5)
    tk.Radiobutton(root, text="Add/Remove Wall", variable=add_mode, value="wall").grid(row=1, column=1, padx=5, pady=5)
    tk.Radiobutton(root, text="Add/Remove Fire", variable=add_mode, value="fire").grid(row=1, column=2, padx=5, pady=5)

    # 상태 표시
    exits_label = tk.Label(root, text="Number of Exits: 0")
    exits_label.grid(row=2, column=0, columnspan=3)
    walls_label = tk.Label(root, text=f"Number of Walls: {len(walls)}")
    walls_label.grid(row=3, column=0, columnspan=3)
    fire_label = tk.Label(root, text="Number of Fire Spots: 0")
    fire_label.grid(row=4, column=0, columnspan=3)
    people_status_label = tk.Label(root, text="Total People: 0, Escaped: 0, Dead: 0, Alive: 0")
    people_status_label.grid(row=5, column=0, columnspan=3)

    # 맵 캔버스
    canvas = tk.Canvas(root, width=map_width * cell_size, height=map_height * cell_size, bg="white")
    canvas.grid(row=0, column=3, rowspan=10, padx=10, pady=10)
    canvas.bind("<Button-1>", on_canvas_click)
    draw_initial_map()

    # 시뮬레이션 시작 버튼
    tk.Button(root, text="Start Simulation", command=start_simulation).grid(row=7, column=0, columnspan=3, pady=10)

    root.mainloop()

# 실행
setup_ui()
