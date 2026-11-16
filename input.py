import time

REPEAT_DELAY = 0.2
REPEAT_RATE = 0.08

prev = {}
hold_start = {}
last_repeat = {}


def is_down(button):
    return not button.value


def pressed(name, button):
    now = is_down(button)
    was = prev.get(name, False)
    prev[name] = now
    return now and not was


def repeat(name, button):
    now = is_down(button)
    was = prev.get(name, False)
    prev[name] = now
    t = time.time()

    if now and not was:
        hold_start[name] = t
        last_repeat[name] = t
        return True

    if now and t - hold_start[name] >= REPEAT_DELAY and t - last_repeat[name] >= REPEAT_RATE:
        last_repeat[name] = t
        return True

    return False


if __name__ == "__main__":
    from joystick import Joystick
    js = Joystick()
    while True:
        if repeat("L", js.button_L):
            print("왼쪽")
        if repeat("R", js.button_R):
            print("오른쪽")
        if repeat("D", js.button_D):
            print("아래")
        if pressed("U", js.button_U):
            print("회전")
        if pressed("A", js.button_A):
            print("A")
        if pressed("B", js.button_B):
            print("B")
        if pressed("C", js.button_C):
            print("교체")
        time.sleep(0.01)