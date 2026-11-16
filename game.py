import random

W = 10
H = 20
HIDDEN = 2
NUM_COLORS = 5

SHAPES = {
    "T": [(-1, 0), (0, 0), (1, 0), (0, 1)],
    "I": [(-1, 0), (0, 0), (1, 0), (2, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "S": [(0, 0), (1, 0), (-1, 1), (0, 1)],
    "Z": [(-1, 0), (0, 0), (0, 1), (1, 1)],
    "J": [(-1, -1), (-1, 0), (0, 0), (1, 0)],
    "L": [(1, -1), (-1, 0), (0, 0), (1, 0)],
}

# 보드 생성
board = []
for _ in range(H + HIDDEN):
    board.append([0] * W)

# 점수
score = 0
LINE_SCORE = [0, 100, 300, 500, 700]

# 현재 도형의 상태 정의
cur_name = None
cur_color = 0
cur_cells = []
cur_x = 0
cur_y = 0


def print_board():
    piece_cells = []
    for x, y in cur_cells:
        piece_cells.append((cur_x + x, cur_y + y))

    for by in range(HIDDEN, H + HIDDEN):
        for bx in range(W):
            if (bx, by) in piece_cells:
                print("■", end=" ")
            elif board[by][bx] != 0:
                print("■", end=" ")
            else:
                print("□", end=" ")
        print()


def random_piece():
    name = random.choice(list(SHAPES.keys()))
    color = random.randint(1, NUM_COLORS)
    return (name, color)


def rotate(cells):
    new_cells = []
    for x, y in cells:
        new_cells.append((y, -x))
    return new_cells


def can_place(cells, px, py):
    for x, y in cells:
        bx = px + x
        by = py + y

        if bx < 0 or bx >= W or by < 0 or by >= H + HIDDEN:
            return False

        if board[by][bx] != 0:
            return False

    return True


def spawn(piece):
    global cur_name, cur_color, cur_cells, cur_x, cur_y
    cur_name, cur_color = piece
    cur_cells = SHAPES[cur_name]
    cur_x = 4
    cur_y = 1
    return can_place(cur_cells, cur_x, cur_y)


def try_move(dx, dy):
    global cur_x, cur_y
    if can_place(cur_cells, cur_x + dx, cur_y + dy):
        cur_x += dx
        cur_y += dy
        return True
    return False

def try_rotate():
    global cur_cells, cur_x
    new_cells = rotate(cur_cells)

    for shift in [0, 1, -1, 2, -2]:
        if can_place(new_cells, cur_x + shift, cur_y):
            cur_cells = new_cells
            cur_x += shift

            return True

    return False

def lock():
    alive = True

    for x, y in cur_cells:
        bx = cur_x + x
        by = cur_y + y
        board[by][bx] = cur_color

        if by < HIDDEN:
            alive = False

    return alive

def clear_lines():
    global board
    new_board = []

    for row in board:
        if 0 in row:
            new_board.append(row)

    cleared = len(board) - len(new_board)

    for _ in range(cleared):
        new_board.insert(0, [0] * W)

    board = new_board

    return cleared

def add_score(cleared):
    global score
    score += LINE_SCORE[cleared]