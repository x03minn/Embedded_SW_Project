import time

# 꾹 누를 때 반복 시작까지 기다리는 시간(초)
REPEAT_DELAY = 0.2
# 반복이 시작된 뒤 반복 간격(초)
REPEAT_RATE = 0.08

# 버튼 이름별 지난번 눌림 상태
prev = {}
# 버튼 이름별 처음 누른 시각
hold_start = {}
# 버튼 이름별 마지막으로 반복된 시각
last_repeat = {}


# 버튼 눌림 판단 함수
def is_down(button):
    """
    버튼은 풀업이라 안 눌리면 True, 눌리면 False이므로
    값을 뒤집어서 눌렸으면 True를 반환.
    """

    return not button.value


# 버튼을 누른 순간 판단 함수
def pressed(name, button):
    """
    지금 눌려 있고 지난번에는 안 눌려 있었을 때만 True 반환.
    꾹 누르고 있어도 누른 순간 한 번만 True가 되어 회전, 하드드롭, 교체 등에 사용.
    """

    now = is_down(button)
    was = prev.get(name, False)
    prev[name] = now

    return now and not was


# 버튼 꾹 누르기 반복 판단 함수
def repeat(name, button):
    """
    누른 순간 True를 반환하고, 계속 누르고 있으면 REPEAT_DELAY가 지난 후부터
    REPEAT_RATE 간격으로 True를 반환. 좌우 이동, 아래 이동에 사용.
    prev를 pressed와 같이 쓰므로 한 버튼은 pressed와 repeat 중 하나로만 읽어야 함.
    """

    now = is_down(button)
    was = prev.get(name, False)
    prev[name] = now
    t = time.time()

    # 방금 누름: 누른 시각을 기록하고 바로 True
    if now and not was:
        hold_start[name] = t
        last_repeat[name] = t
        return True

    # 꾹 누르는 중: 반복 시작 시간이 지났고 반복 간격도 지났으면 True
    if now and t - hold_start[name] >= REPEAT_DELAY and t - last_repeat[name] >= REPEAT_RATE:
        last_repeat[name] = t
        return True

    return False