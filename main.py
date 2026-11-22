import os
import time
from PIL import Image
import game
import render
import input as inp
from joystick import Joystick

# 난이도별 낙하 간격(초): 쉬움 / 보통 / 어려움
FALL_INTERVAL = [0.8, 0.5, 0.25]

# 최고 점수 저장 파일
BEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best.txt')


def load_best():
    try:
        with open(BEST_FILE) as f:
            return int(f.read())
    except (OSError, ValueError):
        return 0


def save_best(score):
    with open(BEST_FILE, 'w') as f:
        f.write(str(score))


# 새 게임 시작하고 낙하 기준 시각 반환
def start_game():
    game.new_game()
    return time.time()


# 떨어지는 블록을 render에 넘길 형식으로
def current_piece():
    cells = [(game.cur_x + x, game.cur_y + y) for x, y in game.cur_cells]
    return {'cells': cells, 'color': game.cur_color}


def game_image(diff):
    return render.draw_game(game.board, current_piece(), game.next_queue, game.score, diff)


js = Joystick()
state = 'start'     # start / play / pause / over
menu = 0
diff = 1
best = load_best()
last_fall = time.time()
dirty = True        # 화면 다시 그려야 하는지
running = True

try:
    while running:
        # 버튼은 상태와 상관없이 매번 읽음 (input.py 이전 상태가 꼬이지 않게)
        up = inp.pressed('U', js.button_U)
        down = inp.repeat('D', js.button_D)
        left = inp.repeat('L', js.button_L)
        right = inp.repeat('R', js.button_R)
        a = inp.pressed('A', js.button_A)
        b = inp.pressed('B', js.button_B)
        c = inp.pressed('C', js.button_C)

        # 시작 화면: 시작하기 / 난이도 / 종료하기
        if state == 'start':
            if up:
                menu = (menu - 1) % 3
                dirty = True
            if down:
                menu = (menu + 1) % 3
                dirty = True
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

        # 게임 중: 좌우 이동 / 아래 빨리 내리기 / 위 바닥까지 / A 회전 / B 바꾸기 / 누르기 일시정지
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

                # 자동 낙하
                if time.time() - last_fall >= FALL_INTERVAL[diff]:
                    game.step()
                    last_fall = time.time()
                    dirty = True

                if game.game_over:
                    if game.score > best:
                        best = game.score
                        save_best(best)
                    state = 'over'
                    menu = 0
                    dirty = True

        # 일시정지: 계속하기 / 다시 시작 / 처음 화면으로
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

        # 게임 오버: 다시 하기 / 처음 화면으로
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

        # 바뀐 게 있을 때만 다시 그림
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

# 끝나면 화면 검게
js.disp.image(Image.new('RGB', (240, 240), (0, 0, 0)))
print('게임 종료')