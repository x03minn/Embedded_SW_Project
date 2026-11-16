import time
import game
import render
import input as inp
from joystick import Joystick

FALL_INTERVAL = 0.5

js = Joystick()
game.new_game()
paused = False
last_fall = time.time()

while True:
    if game.game_over:
        render.draw(js)
        if inp.pressed("A", js.button_A):
            game.new_game()
            last_fall = time.time()
        time.sleep(0.05)
        continue

    if inp.pressed("B", js.button_B):
        paused = not paused

    if paused:
        render.draw(js, paused)
        time.sleep(0.05)
        continue

    if inp.repeat("L", js.button_L):
        game.try_move(-1, 0)
    if inp.repeat("R", js.button_R):
        game.try_move(1, 0)
    if inp.repeat("D", js.button_D):
        game.step()
        last_fall = time.time()
    if inp.pressed("U", js.button_U):
        game.try_rotate()
    if inp.pressed("A", js.button_A):
        game.hard_drop()
        last_fall = time.time()
    if inp.pressed("C", js.button_C):
        game.swap_next()

    if time.time() - last_fall >= FALL_INTERVAL:
        game.step()
        last_fall = time.time()

    render.draw(js)