import os
import time
from PIL import Image
import game
import render
import input as inp
from joystick import Joystick

# 난이도별 블럭 떨어지는 간격 (쉬움 / 보통 / 어려움, 초)
FALL_INTERVAL = [0.8, 0.5, 0.25]

# 줄 하나 지울 때마다 간격 줄이는 비율, 최소 간격 (초)
SPEED_UP = 0.98
MIN_INTERVAL = 0.1

# 최고 점수 저장 파일
BEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best.txt')


# 최고 점수 불러오기 함수
def load_best():
    """
    파일에서 최고 점수를 읽어서 반환. 파일이 없으면 0.
    """

    try:
        with open(BEST_FILE) as f:
            return int(f.read())
    except (OSError, ValueError):
        return 0


# 최고 점수 저장 함수
def save_best(score):
    """
    최고 점수를 파일에 저장.
    """

    with open(BEST_FILE, 'w') as f:
        f.write(str(score))


# 게임 시작 함수
def start_game():
    """
    새 게임을 시작하고 현재 시간 반환.
    """

    game.new_game()
    return time.time()


# 현재 블럭 정보 함수
def current_piece():
    """
    현재 블럭의 보드 좌표, 색, 아이템을 딕셔너리로 반환.
    """

    cells = [(game.cur_x + x, game.cur_y + y) for x, y in game.cur_cells]
    return {'cells': cells, 'color': game.cur_color,
            'item': game.cur_item, 'item_idx': game.cur_item_idx}


# 게임 화면 함수
def game_image(diff):
    """
    현재 게임 화면 이미지 반환.
    """

    return render.draw_game(game.board, current_piece(), game.next_queue, game.score, diff)


# 낙하 간격 함수
def fall_interval(diff):
    """
    지운 줄이 많을수록 조금씩 빨라짐. 최소 간격보다는 안 빨라짐.
    """

    interval = FALL_INTERVAL[diff] * (SPEED_UP ** game.lines)
    return max(MIN_INTERVAL, interval)


js = Joystick()

# 화면 상태 (start / play / pause / over)
state = 'start'
menu = 0
diff = 1
best = load_best()
last_fall = time.time()

# 화면을 다시 그려야 하는지
dirty = True
running = True

try:
    while running:
        # 버튼 입력 (상태 상관없이 매번 읽음)
        up = inp.pressed('U', js.button_U)
        down = inp.repeat('D', js.button_D)
        left = inp.repeat('L', js.button_L)
        right = inp.repeat('R', js.button_R)
        a = inp.pressed('A', js.button_A)
        b = inp.pressed('B', js.button_B)
        c = inp.pressed('C', js.button_C)

        # 시작 화면
        if state == 'start':
            if up:
                menu = (menu - 1) % 3
                dirty = True
            if down:
                menu = (menu + 1) % 3
                dirty = True

            # 난이도 조절
            if menu == 1 and left and diff > 0:
                diff -= 1
                dirty = True
            if menu == 1 and right and diff < 2:
                diff += 1
                dirty = True

            if a or c:
                if menu == 0:
                    last_fall = start_game()
                    state = 'play'
                    dirty = True
                elif menu == 2:
                    running = False

        # 게임 화면
        elif state == 'play':
            if c:
                state = 'pause'
                menu = 0
                dirty = True
            else:
                if left:
                    game.try_move(-1, 0)
                    dirty = True
                if right:
                    game.try_move(1, 0)
                    dirty = True
                if down:
                    game.step()
                    last_fall = time.time()
                    dirty = True
                if up:
                    game.hard_drop()
                    last_fall = time.time()
                    dirty = True
                if a:
                    game.try_rotate()
                    dirty = True
                if b:
                    game.swap_next()
                    dirty = True

                # 시간 되면 한 칸 내리기
                if time.time() - last_fall >= fall_interval(diff):
                    game.step()
                    last_fall = time.time()
                    dirty = True

                # 게임 오버
                if game.game_over:
                    if game.score > best:
                        best = game.score
                        save_best(best)
                    state = 'over'
                    menu = 0
                    dirty = True

        # 일시정지 화면
        elif state == 'pause':
            if up:
                menu = (menu - 1) % 3
                dirty = True
            if down:
                menu = (menu + 1) % 3
                dirty = True
            if a or c:
                if menu == 0:
                    last_fall = time.time()
                    state = 'play'
                elif menu == 1:
                    last_fall = start_game()
                    state = 'play'
                else:
                    state = 'start'
                    menu = 0
                dirty = True

        # 게임 오버 화면
        elif state == 'over':
            if up or down:
                menu = 1 - menu
                dirty = True
            if a or c:
                if menu == 0:
                    last_fall = start_game()
                    state = 'play'
                else:
                    state = 'start'
                    menu = 0
                dirty = True

        # 바뀐 게 있을 때만 화면 그리기
        if dirty and running:
            if state == 'start':
                img = render.draw_start(menu, diff)
            elif state == 'play':
                img = game_image(diff)
            elif state == 'pause':
                img = render.draw_pause(game_image(diff), game.score, menu)
            else:
                img = render.draw_game_over(game_image(diff), game.score, best, diff, menu)
            js.disp.image(img)
            dirty = False

        time.sleep(0.01)

except KeyboardInterrupt:
    pass

# 종료하면 화면 끄기
js.disp.image(Image.new('RGB', (240, 240), (0, 0, 0)))
print('게임 종료')