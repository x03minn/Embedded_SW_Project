import random

# 보드 크기랑 블럭 색 개수
W = 10
H = 20
HIDDEN = 2
NUM_COLORS = 5

# 블럭 모양
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

# 점수, 지운 줄 수
score = 0
lines = 0
LINE_SCORE = [0, 100, 300, 500, 800]

# 다음 블럭 큐
NEXT_COUNT = 4
next_queue = []

# 게임 상태
game_over = False

# 현재 블럭
cur_name = None
cur_color = 0
cur_item = 0
cur_item_idx = 0
cur_cells = []
cur_x = 0
cur_y = 0

# 아이템 확률 (%)
ITEM_PERCENT = 5

# 1.점수 2배 2.세로줄 3.폭탄 4.색상 제거
NUM_ITEMS = 4


# 보드 출력 함수
def print_board():
    """
    블럭이 있는 칸은 ■, 빈칸은 □로 출력.
    숨겨진 줄은 제외하고 출력.
    """

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


# 랜덤 블럭 함수
def random_piece():
    """
    블럭 모양, 색, 아이템을 랜덤으로 정해서 반환.
    ITEM_PERCENT 확률로 한 칸에 아이템이 붙음.
    """

    item = 0
    item_idx = 0

    k = random.randint(1, 100)

    if k <= ITEM_PERCENT:
        item = random.randint(1, NUM_ITEMS)
        item_idx = random.randint(0, 3)

    name = random.choice(list(SHAPES.keys()))
    color = random.randint(1, NUM_COLORS)

    return (name, color, item, item_idx)


# 블럭 회전 함수
def rotate(cells):
    """
    (0, 0) 기준으로 회전한 좌표 반환.
    """

    new_cells = []

    for x, y in cells:
        new_cells.append((y, -x))

    return new_cells


# 블럭 배치 확인 함수
def can_place(cells, px, py):
    """
    해당 위치에 블럭을 놓을 수 있으면 True, 없으면 False.
    """

    for x, y in cells:
        bx = px + x
        by = py + y

        if bx < 0 or bx >= W or by < 0 or by >= H + HIDDEN:
            return False

        if board[by][bx] != 0:
            return False

    return True


# 블럭 생성 함수
def spawn(piece):
    """
    받은 블럭을 현재 블럭으로 설정하고 시작 위치에 놓음.
    놓을 수 없으면 False.
    """

    global cur_name, cur_color, cur_item, cur_item_idx, cur_cells, cur_x, cur_y
    cur_name, cur_color, cur_item, cur_item_idx = piece
    cur_cells = SHAPES[cur_name]
    cur_x = 4
    cur_y = 1

    return can_place(cur_cells, cur_x, cur_y)


# 블럭 이동 함수
def try_move(dx, dy):
    """
    블럭을 이동. 이동하면 True, 못 하면 False.
    """

    global cur_x, cur_y

    if can_place(cur_cells, cur_x + dx, cur_y + dy):
        cur_x += dx
        cur_y += dy

        return True

    return False


# 블럭 회전 함수
def try_rotate():
    """
    블럭을 회전. 막히면 옆으로 밀어서 다시 시도.
    회전하면 True, 못 하면 False.
    """

    global cur_cells, cur_x
    new_cells = rotate(cur_cells)

    for shift in [0, 1, -1, 2, -2]:
        if can_place(new_cells, cur_x + shift, cur_y):
            cur_cells = new_cells
            cur_x += shift

            return True

    return False


# 블럭 고정 함수
def lock():
    """
    블럭을 보드에 고정. 아이템 칸은 색 + 아이템 * 10 으로 저장.
    숨겨진 줄에 고정되면 False.
    """

    alive = True

    for i, (x, y) in enumerate(cur_cells):
        bx = cur_x + x
        by = cur_y + y

        value = cur_color

        if cur_item and i == cur_item_idx:
            value += cur_item * 10

        board[by][bx] = value

        if by < HIDDEN:
            alive = False

    return alive


# 아이템 효과 범위 함수
def item_cells(item, x, y, color):
    """
    아이템 효과로 지울 칸 반환.
    세로줄은 한 열, 폭탄은 주변 3x3, 색상 제거는 같은 색 전부.
    """

    cells = []

    if item == 2:
        for by in range(H + HIDDEN):
            if board[by][x]:
                cells.append((x, by))

    elif item == 3:
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                bx = x + dx
                by = y + dy
                if 0 <= bx < W and 0 <= by < H + HIDDEN and board[by][bx]:
                    cells.append((bx, by))

    elif item == 4:
        for by in range(H + HIDDEN):
            for bx in range(W):
                v = board[by][bx]
                if v and v % 10 == color:
                    cells.append((bx, by))

    return cells


# 줄 삭제 함수
def clear_lines():
    """
    꽉 찬 줄과 아이템 효과로 지울 칸을 지움.
    지운 줄 수와 점수 배율 반환.
    """

    global board

    # 꽉 찬 줄 찾기
    full_rows = []
    for y in range(H + HIDDEN):
        if 0 not in board[y]:
            full_rows.append(y)

    # 꽉 찬 줄의 칸 모으기
    to_clear = set()
    for y in full_rows:
        for x in range(W):
            to_clear.add((x, y))

    # 지울 칸의 아이템을 큐에 넣기
    queue = []
    for x, y in to_clear:
        if board[y][x] // 10:
            queue.append((x, y))

    # 아이템 연쇄 처리
    mult = 1
    while queue:
        x, y = queue.pop(0)
        item = board[y][x] // 10
        color = board[y][x] % 10

        if item == 1:
            mult *= 2

        for cx, cy in item_cells(item, x, y, color):
            # 중복 방지
            if (cx, cy) not in to_clear:
                to_clear.add((cx, cy))
                if board[cy][cx] // 10:
                    queue.append((cx, cy))

    # 아이템으로 지운 칸 비우기
    for x, y in to_clear:
        if y not in full_rows:
            board[y][x] = 0

    # 꽉 찬 줄 제거 후 위에 빈 줄 추가
    new_board = []
    for y in range(H + HIDDEN):
        if y not in full_rows:
            new_board.append(board[y])

    cleared = len(full_rows)
    for _ in range(cleared):
        new_board.insert(0, [0] * W)

    board = new_board
    return cleared, mult


# 점수 추가 함수
def add_score(cleared, mult = 1):
    """
    지운 줄 수와 배율에 따라 점수 추가.
    """

    global score
    score += LINE_SCORE[cleared] * mult


# 블럭 큐 생성 함수
def fill_queue():
    """
    큐를 비우고 새 블럭으로 채움.
    """

    next_queue.clear()

    for _ in range(NEXT_COUNT):
        next_queue.append(random_piece())


# 다음 블럭 함수
def next_piece():
    """
    큐에서 다음 블럭을 꺼내고 새 블럭 추가.
    """

    piece = next_queue.pop(0)
    next_queue.append(random_piece())
    return piece


# 블럭 교체 함수
def swap_next():
    """
    현재 블럭과 다음 블럭을 교체.
    교체하면 True, 못 하면 False.
    """

    global cur_name, cur_color, cur_item, cur_item_idx, cur_cells
    new_name, new_color, new_item, new_item_idx = next_queue[0]
    new_cells = SHAPES[new_name]

    if not can_place(new_cells, cur_x, cur_y):
        return False

    next_queue[0] = (cur_name, cur_color, cur_item, cur_item_idx)
    cur_name = new_name
    cur_color = new_color
    cur_item = new_item
    cur_item_idx = new_item_idx
    cur_cells = new_cells
    return True


# 새 게임 함수
def new_game():
    """
    게임 초기화 후 첫 블럭 생성.
    """

    global board, score, lines, game_over
    board = []
    for _ in range(H + HIDDEN):
        board.append([0] * W)
    score = 0
    lines = 0
    game_over = False
    fill_queue()
    spawn(next_piece())


# 착지 처리 함수
def settle():
    """
    블럭 고정, 줄 삭제, 점수 추가, 지운 줄 수 누적 후 다음 블럭 생성.
    더 이상 진행할 수 없으면 게임 오버.
    """

    global game_over, lines
    alive = lock()
    cleared, mult = clear_lines()
    add_score(cleared, mult)
    lines += cleared

    if not alive or not spawn(next_piece()):
        game_over = True


# 블럭 내리기 함수
def step():
    """
    한 칸 내리고, 못 내려가면 착지 처리.
    """

    if not try_move(0, 1):
        settle()


# 하드 드롭 함수
def hard_drop():
    """
    바닥까지 내리고 착지 처리.
    """

    while try_move(0, 1):
        pass
    settle()