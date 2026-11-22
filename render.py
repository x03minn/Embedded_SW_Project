import os
from PIL import Image, ImageDraw, ImageFont
from game import SHAPES, HIDDEN

# 화면 크기, 한 칸 크기, 보드 칸 수
W = H = 240
CELL = 12
COLS, ROWS = 10, 20

# 화면 색
BG      = (243, 242, 238)
CELL_BG = (233, 234, 236)
INK     = (31, 35, 41)
SUB     = (94, 99, 107)
ACCENT  = (74, 104, 217)
WHITE   = (255, 255, 255)
BTN_TXT = (61, 65, 72)
LINE    = (218, 220, 224)
DOT_OFF = (205, 208, 214)

# 블럭 색 (색 번호 1~5)
BLOCK_COLOR = {
    1: (217, 138, 138),
    2: (134, 181, 211),
    3: (232, 196, 109),
    4: (155, 205, 180),
    5: (181, 161, 214),
}

# 난이도 이름
DIFFICULTIES = ['쉬움', '보통', '어려움']

# 한글 폰트 경로 (나눔고딕 없으면 노토)
_FONT_PATHS = {
    'regular': ['/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'],
    'bold':    ['/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'],
    'heavy':   ['/usr/share/fonts/truetype/nanum/NanumGothicExtraBold.ttf',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'],
}
_font_cache = {}


# 폰트 함수
def font(size, weight='regular'):
    """
    크기와 굵기에 맞는 폰트 반환. 한 번 연 폰트는 저장해두고 다시 씀.
    """

    key = (size, weight)
    if key not in _font_cache:
        for path in _FONT_PATHS[weight]:
            try:
                _font_cache[key] = ImageFont.truetype(path, size)
                break
            except OSError:
                continue
        else:
            raise RuntimeError('한글 폰트가 없음: sudo apt install fonts-nanum')
    return _font_cache[key]


# 칸 그리기 함수
def _cell(d, x, y, s, color, r=2):
    d.rounded_rectangle((x, y, x + s - 1, y + s - 1), radius=r, fill=color)


# 아이템 아이콘 (icons 폴더)
# 1.점수 2배 2.세로줄 3.폭탄 4.색상 제거
ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
ICON_FILES = {1: 'x2.png', 2: 'line.png', 3: 'bomb.png', 4: 'color.png'}
_icon_cache = {}


# 아이콘 불러오기 함수
def _icon(file, size):
    """
    아이콘을 칸 크기에 맞게 줄여서 반환. 한 번 만든 건 저장해두고 다시 씀.
    """

    key = (file, size)
    if key not in _icon_cache:
        im = Image.open(os.path.join(ICON_DIR, file)).convert('RGBA')
        if im.size != (size, size):
            im = im.resize((size, size), Image.NEAREST if size >= im.width else Image.LANCZOS)
        _icon_cache[key] = im
    return _icon_cache[key]


# 아이콘 그리기 함수
def _item_icon(img, x, y, s, item):
    """
    칸 가운데에 아이콘을 붙임. 투명한 부분은 블럭 색이 그대로 보임.
    """

    size = max(5, s - 2)
    icon = _icon(ICON_FILES[item], size)
    off = (s - size) // 2
    img.paste(icon, (x + off, y + off), icon)


# 좌표 정리 함수
def _norm(cells):
    """
    블럭 좌표를 0부터 시작하게 옮겨서 반환.
    """

    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    return [(x - mx, y - my) for x, y in cells]


# 블럭 그리기 함수
def _piece(img, name, color, cx, cy, s, gap, r=2, item=0, item_idx=0):
    """
    (cx, cy)가 가운데가 되게 블럭을 그림. 다음 블럭, 로고에 씀.
    """

    d = ImageDraw.Draw(img)
    cells = _norm(SHAPES[name])
    w = max(x for x, _ in cells) + 1
    h = max(y for _, y in cells) + 1
    pw, ph = w * s + (w - 1) * gap, h * s + (h - 1) * gap
    x0, y0 = cx - pw // 2, cy - ph // 2
    for i, (x, y) in enumerate(cells):
        px, py = x0 + x * (s + gap), y0 + y * (s + gap)
        _cell(d, px, py, s, BLOCK_COLOR[color], r)
        if item and i == item_idx:
            _item_icon(img, px, py, s, item)


# 가운데 정렬 글자 함수
def _ctext(d, cx, cy, text, size, weight='regular', color=INK):
    d.text((cx, cy), text, font=font(size, weight), fill=color, anchor='mm')


# 버튼 그리기 함수
def _button(d, x, y, w, h, label, selected, size=12):
    """
    선택된 버튼은 파란색, 아니면 회색.
    """

    d.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=8,
                        fill=ACCENT if selected else CELL_BG)
    _ctext(d, x + w // 2, y + h // 2, label, size, 'bold',
           WHITE if selected else BTN_TXT)


# 화면 어둡게 하는 함수
def _dim(img):
    """
    팝업 뒤에 깔 수 있게 화면을 어둡게 해서 반환.
    """

    overlay = Image.new('RGBA', img.size, (31, 35, 41, 140))
    return Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')


# 시작 화면 함수
def draw_start(menu_index=0, difficulty=1):
    """
    로고와 메뉴(시작하기 / 난이도 / 종료하기) 화면 반환.
    """

    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # 로고 블럭
    logo = [('T', 2), ('S', 4), ('L', 3), ('O', 1), ('Z', 5)]
    x = 41
    for name, color in logo:
        cells = _norm(SHAPES[name])
        w = max(c for c, _ in cells) + 1
        pw = w * 8 + (w - 1)
        _piece(img, name, color, x + pw // 2, 34, 8, 1)
        x += pw + 6

    _ctext(d, 120, 79, 'PiTris', 30, 'heavy')

    bx, bw, bh = 34, 172, 32
    _button(d, bx, 116, bw, bh, '시작하기', menu_index == 0, 13)

    # 난이도 칸 (선택되면 테두리 파란색)
    y = 154
    d.rounded_rectangle((bx, y, bx + bw - 1, y + bh - 1), radius=8, fill=WHITE,
                        outline=ACCENT if menu_index == 1 else LINE,
                        width=2 if menu_index == 1 else 1)
    _ctext(d, bx + 13, y + 16, '‹', 16, 'bold', SUB)
    _ctext(d, bx + bw - 13, y + 16, '›', 16, 'bold', SUB)
    _ctext(d, 120, y + 13, DIFFICULTIES[difficulty], 13, 'bold', ACCENT)

    # 난이도 표시 점
    dx = 120 - 12
    for i in range(3):
        on = i == difficulty
        w = 10 if on else 4
        d.rounded_rectangle((dx, y + 24, dx + w - 1, y + 27), radius=2,
                            fill=ACCENT if on else DOT_OFF)
        dx += w + 3

    _button(d, bx, 192, bw, bh, '종료하기', menu_index == 2, 13)
    return img


# 게임 화면 함수
def draw_game(board, current=None, queue=(), score=0, difficulty=1):
    """
    보드, 현재 블럭, 점수, 난이도, 다음 블럭 화면 반환.
    """

    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # 보드 (숨겨진 줄은 안 그림)
    d.rectangle((0, 0, COLS * CELL - 1, ROWS * CELL - 1), fill=CELL_BG)
    for by in range(HIDDEN, HIDDEN + ROWS):
        for bx, v in enumerate(board[by]):
            if v:
                _cell(d, bx * CELL, (by - HIDDEN) * CELL, CELL - 1, BLOCK_COLOR[v % 10])
                if v // 10:
                    _item_icon(img, bx * CELL, (by - HIDDEN) * CELL, CELL - 1, v // 10)

    # 현재 블럭
    if current:
        for i, (x, y) in enumerate(current['cells']):
            sy = y - HIDDEN
            if 0 <= sy < ROWS:
                _cell(d, x * CELL, sy * CELL, CELL - 1, BLOCK_COLOR[current['color']])
                if current['item'] and i == current['item_idx']:
                    _item_icon(img, x * CELL, sy * CELL, CELL - 1, current['item'])

    # 점수, 난이도
    px, pw = 128, 104
    f10 = font(10, 'bold')
    d.text((px, 10), '점수', font=f10, fill=SUB)
    d.text((px, 24), f'{score:,}', font=font(20, 'heavy'), fill=INK)
    d.text((px, 54), '난이도', font=f10, fill=SUB)
    d.text((px + 40, 53), DIFFICULTIES[difficulty], font=font(12, 'bold'), fill=ACCENT)
    d.text((px, 76), '다음', font=f10, fill=SUB)

    queue = list(queue)

    # 다음 블럭 (B로 교체 가능)
    d.rounded_rectangle((px, 90, px + pw - 1, 143), radius=8, fill=WHITE,
                        outline=ACCENT, width=2)
    d.ellipse((px + 6, 96, px + 19, 109), fill=ACCENT)
    _ctext(d, px + 13, 103, 'B', 9, 'heavy', WHITE)
    if queue:
        name, color, item, item_idx = queue[0]
        _piece(img, name, color, px + pw // 2, 117, 11, 1, item=item, item_idx=item_idx)

    # 그 다음 블럭 3개
    for i in range(3):
        by = 150 + i * 30
        d.rounded_rectangle((px, by, px + pw - 1, by + 25), radius=6, fill=CELL_BG)
        if len(queue) > i + 1:
            name, color, item, item_idx = queue[i + 1]
            _piece(img, name, color, px + pw // 2, by + 13, 7, 1, r=1, item=item, item_idx=item_idx)
    return img


# 일시정지 화면 함수
def draw_pause(game_img, score, menu_index=0):
    """
    게임 화면 위에 일시정지 팝업(계속하기 / 다시 시작 / 처음 화면으로)을 띄워서 반환.
    """

    img = _dim(game_img)
    d = ImageDraw.Draw(img)
    px, pw = 30, 180
    d.rounded_rectangle((px, 38, px + pw - 1, 201), radius=14, fill=WHITE)
    _ctext(d, 120, 60, '일시정지', 16, 'heavy')
    _ctext(d, 120, 81, f'점수 {score:,}', 10, 'bold', SUB)
    for i, label in enumerate(['계속하기', '다시 시작', '처음 화면으로']):
        _button(d, px + 12, 98 + i * 34, pw - 24, 28, label, menu_index == i)
    return img


# 게임 오버 화면 함수
def draw_game_over(game_img, score, best, difficulty=1, menu_index=0):
    """
    게임 화면 위에 게임 오버 팝업(점수, 최고 점수, 다시 하기 / 처음 화면으로)을 띄워서 반환.
    """

    img = _dim(game_img)
    d = ImageDraw.Draw(img)
    px, pw = 30, 180
    d.rounded_rectangle((px, 20, px + pw - 1, 219), radius=14, fill=WHITE)

    # 색 블럭 장식
    for i in range(5):
        _cell(d, 120 - 26 + i * 11, 32, 9, BLOCK_COLOR[i + 1])

    _ctext(d, 120, 58, '게임 오버', 16, 'heavy')
    _ctext(d, 120, 81, '최종 점수', 10, 'bold', SUB)
    _ctext(d, 120, 103, f'{score:,}', 26, 'heavy', ACCENT)

    # 최고 점수, 난이도
    bx, bw = px + 12, pw - 24
    d.rounded_rectangle((bx, 124, bx + bw - 1, 155), radius=8, fill=BG)
    half = bw // 2
    _ctext(d, bx + half // 2, 134, '최고 점수', 9, 'bold', SUB)
    _ctext(d, bx + half // 2, 147, f'{best:,}', 11, 'bold')
    _ctext(d, bx + half + half // 2, 134, '난이도', 9, 'bold', SUB)
    _ctext(d, bx + half + half // 2, 147, DIFFICULTIES[difficulty], 11, 'bold')

    _button(d, bx, 164, bw, 22, '다시 하기', menu_index == 0, 11)
    _button(d, bx, 190, bw, 22, '처음 화면으로', menu_index == 1, 11)
    return img