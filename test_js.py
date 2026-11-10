import joystick as j
from PIL import Image, ImageDraw
import time

joystick = j.Joystick()
img = Image.new("RGB", (240, 240), "green")
draw = ImageDraw.Draw(img)

while True:
    img = Image.new("RGB", (240, 240), "green")
    joystick.disp.image(img)

    if not joystick.button_A.value == True:
        img = Image.new("RGB", (240, 240), "red")

    joystick.disp.image(img)
