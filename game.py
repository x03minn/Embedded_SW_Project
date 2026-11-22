import random

# 보드의 크기 및 블럭 색상 갯수
W = 10
H = 20
HIDDEN = 2
NUM_COLORS = 5

# 블록의 모양
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
LINE_SCORE = [0, 100, 300, 500, 800]

# 블록 큐
NEXT_COUNT = 4
next_queue = []

# 게임 상태
game_over = False

# 현재 도형의 상태 정의
cur_name = None
cur_color = 0
cur_item = 0
cur_item_idx = 0
cur_cells = []
cur_x = 0
cur_y = 0

# 아이템 등장 확률
ITEM_PERCENT = 5

# 1.점수 2배 2.세로줄 3.폭탄 4. 색상 제거 
NUM_ITEMS = 4

# 현재 보드 출력 함수
def print_board():
    """
    현재 블럭의 모양을 가지고 현재 좌표에 상대좌표를 더한 값을 튜플 형태로 리스트에 저장
    떨어지고 있는 블럭이나, 이미 굳어진 블럭은 "■"으로 나머지는 "□"으로 출력한다.
    출력은 2번 인덱스 부터 21번 인덱스 까지 출력한다.
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


# 랜덤한 블럭 선택 함수
def random_piece():
    """
    랜덤하게 블럭 이름, 색상, 아이템, 아이템 칸 번호를 튜플로 반환.
    ITEM_PERCENT% 확률로 아이템(1~4)이 4칸 중 한 칸에 붙고, 없으면 아이템은 0.
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
    새로운 리스트를 만들고, 블럭의 상대좌표 (0, 0)을 축으로 반시계 방향으로 회전 한 좌표 반환.
    """

    new_cells = []
    
    for x, y in cells:
        new_cells.append((y, -x))

    return new_cells


# 블럭 배치 판단 함수
def can_place(cells, px, py):
    """
    현재 블럭의 상대좌표와, 기준 좌표를 받아서 그 값이 범위를 벗어나거나 굳어진 블럭이 있으면 False를 아니면 True를 반환.
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
    현재 블럭의 이름과 색상, 상대좌표, 현재 좌표를 생성할 블럭으로 초기화 시키고, 배치할 위치에 블럭이 이미 있으면 False 반환.
    """

    global cur_name, cur_color, cur_item, cur_item_idx, cur_cells, cur_x, cur_y
    cur_name, cur_color, cur_item, cur_item_idx = piece
    cur_cells = SHAPES[cur_name]
    cur_x = 4
    cur_y = 1

    return can_place(cur_cells, cur_x, cur_y)


# 블럭 이동 판단 함수
def try_move(dx, dy):
    """
    이동량을 인자로 받아서 현재 블럭의 좌표에 더한 값이 배치 가능하면 현재 좌표에 더한 값으로 갱신하고 True를 반환 아니면 False 반환.
    """

    global cur_x, cur_y

    if can_place(cur_cells, cur_x + dx, cur_y + dy):
        cur_x += dx
        cur_y += dy

        return True
    
    return False


# 블럭 회전 판단 함수
def try_rotate():
    """
    현재 블럭의 상대 좌표와 현재 x좌표, 현재 블럭을 회전한 블럭을 가지고, 배치할 수 있는 칸으로 블럭 배치를 하고 배치가 되면 True 안되면 False 반환.
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
    현재 블럭의 상대좌표와 현재 좌표를 이용하여 현재 블럭의 색상번호로 보드를 변경.
    아이템 칸은 색상번호 + 아이템 * 10 으로 저장.
    만약 블럭의 좌표 중 HIDDEN 보다 낮은 y좌표가 있을 경우 alive를 False로 변경 후 반환.
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
    (x, y)에 있는 아이템이 터질 때 지울 블럭 좌표 리스트를 반환. 빈칸은 넣지 않음.
    1 점수 2배: 없음 / 2 세로줄: 그 열 전부 / 3 폭탄: 주변 3x3 / 4 색상 제거: 같은 색 전부
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


# 채워진 줄 처리 함수
def clear_lines():
    """
    꽉 찬 줄과 아이템으로 지울 칸을 to_clear에 모은 뒤 한 번에 지움.
    꽉 찬 줄이 아닌 칸은 0으로 비우고(공중에 떠도 둠), 꽉 찬 줄은 빼고 위에 빈 줄을 추가.
    (지운 줄 수, 점수 배율) 반환.
    """

    global board

    # 1. 꽉 찬 줄 찾기
    full_rows = []
    for y in range(H + HIDDEN):
        if 0 not in board[y]:
            full_rows.append(y)

    # 2. 꽉 찬 줄의 칸을 지울 칸에 모으기
    to_clear = set()
    for y in full_rows:
        for x in range(W):
            to_clear.add((x, y))

    # 3. 지울 칸 중 아이템 칸을 큐에 넣기
    queue = []
    for x, y in to_clear:
        if board[y][x] // 10:
            queue.append((x, y))

    # 4. 큐에서 하나씩 꺼내서 터뜨리기 (연쇄)
    mult = 1
    while queue:
        x, y = queue.pop(0)
        item = board[y][x] // 10
        color = board[y][x] % 10

        if item == 1:
            mult *= 2

        for cx, cy in item_cells(item, x, y, color):
            if (cx, cy) not in to_clear:
                to_clear.add((cx, cy))
                if board[cy][cx] // 10:
                    queue.append((cx, cy))

    # 5. 꽉 찬 줄이 아닌 칸은 0으로
    for x, y in to_clear:
        if y not in full_rows:
            board[y][x] = 0

    # 6. 꽉 찬 줄 빼고 위에 빈 줄 추가
    new_board = []
    for y in range(H + HIDDEN):
        if y not in full_rows:
            new_board.append(board[y])

    cleared = len(full_rows)
    for _ in range(cleared):
        new_board.insert(0, [0] * W)

    board = new_board
    return cleared, mult


# 점수 더하기 함수
def add_score(cleared, mult = 1):
    """
    지운 줄 수와 배율을 받아서 LINE_SCORE에 따라 점수를 더함. 한 번에 많은 행을 지우면 높은 점수.
    """

    global score
    score += LINE_SCORE[cleared] * mult


# 블럭 큐 생성 함수
def fill_queue():
    """
    기존 큐를 초기화 시키고, 큐 길이만큼 블럭을 생성해 큐에 넣어놓는다.
    """

    next_queue.clear()

    for _ in range(NEXT_COUNT):
        next_queue.append(random_piece())


# 다음 블럭 생성 함수
def next_piece():
    """
    기존 큐에 front를 블럭에 넣고, 제거 후 새로운 블럭을 큐의 rear에 넣는다.
    블럭을 반환.
    """

    piece = next_queue.pop(0)
    next_queue.append(random_piece())
    return piece


# 다음 블럭과 스위칭 함수
def swap_next():
    """
    현재 블럭을 다음 블럭과 교체. 만약 교체 블럭이 놓일 수 없으면 False 반환.
    교체 후 블럭을 현재 블럭으로 초기화 시키고 True 반환.
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


# 게임 생성 함수
def new_game():
    """
    전역 보드, 점수, 게임 상태를 초기화 시키고, 블럭 큐와 다음 생성할 블럭 생성.
    """

    global board, score, game_over
    board = []
    for _ in range(H + HIDDEN):
        board.append([0] * W)
    score = 0
    game_over = False
    fill_queue()
    spawn(next_piece())


# 블럭 착지 처리 함수
def settle():
    """
    주워진 줄의 갯수만큼 점수를 더해주고, 고정된 블럭 좌표를 기반으로 만약 죽었거나 다음 블럭이 생성될 수 없다면, 게임 오버.
    """

    global game_over
    alive = lock()
    cleared, mult = clear_lines()
    add_score(cleared, mult)

    if not alive or not spawn(next_piece()):
        game_over = True


# 블럭 이동 함수
def step():
    """ 
    블럭 이동이 안되면 블럭 착지 처리 함수 불러오기.
    """

    if not try_move(0, 1):
        settle()


# 블럭을 바로 떨어뜨리는 함수
def hard_drop():
    """
    블럭을 계속 아래로 이동 시키고 이동이 안되면 블럭 착지 처리 함수 불러오기.
    """

    while try_move(0, 1):
        pass
    settle()