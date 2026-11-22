import time

# 꾹 누를 때 반복 시작까지 시간, 반복 간격 (초)
REPEAT_DELAY = 0.2
REPEAT_RATE = 0.08

# 버튼별 이전 상태, 누르기 시작한 시간, 마지막 반복 시간
prev = {}
hold_start = {}
last_repeat = {}


# 버튼 눌림 확인 함수
def is_down(button):
    """
    버튼이 눌려있으면 True. (누르면 값이 0이라 반대로 반환)
    """

    return not button.value


# 버튼 한 번 입력 함수
def pressed(name, button):
    """
    버튼을 누른 순간에만 True. 계속 누르고 있어도 한 번만 입력.
    """

    now = is_down(button)
    was = prev.get(name, False)
    prev[name] = now
    return now and not was


# 버튼 반복 입력 함수
def repeat(name, button):
    """
    누른 순간 True, 꾹 누르고 있으면 일정 시간 뒤부터 반복해서 True.
    """

    now = is_down(button)
    was = prev.get(name, False)
    prev[name] = now
    t = time.time()

    # 처음 누른 순간
    if now and not was:
        hold_start[name] = t
        last_repeat[name] = t
        return True

    # 꾹 누르고 있을 때 반복
    if now and t - hold_start[name] >= REPEAT_DELAY and t - last_repeat[name] >= REPEAT_RATE:
        last_repeat[name] = t
        return True

    return False