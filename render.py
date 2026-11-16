from PIL import Image, ImageDraw
import game

CELL = 12
SMALL = 6
PANEL_X = game.W * CELL

PALETTE = {
    0: (25, 25, 25),
    1: (255, 80, 80),
    2: (80, 200, 255),
    3: (255, 220, 60),
    4: (120, 230, 120),
    5: (200, 120, 255),
}


def draw_cell(d, sx, sy, color, size):
    d.rectangle((sx, sy, sx + size - 2, sy + size - 2), fill=color)


def draw(js):
    img = Image.new("RGB", (js.width, js.height), (0, 0, 0))
    d = ImageDraw.Draw(img)

    for by in range(game.HIDDEN, game.H + game.HIDDEN):
        for bx in range(game.W):
            v = game.board[by][bx]
            sx = bx * CELL
            sy = (by - game.HIDDEN) * CELL
            draw_cell(d, sx, sy, PALETTE[v % 10], CELL)

    for x, y in game.cur_cells:
        bx = game.cur_x + x
        by = game.cur_y + y
        if by >= game.HIDDEN:
            draw_cell(d, bx * CELL, (by - game.HIDDEN) * CELL, PALETTE[game.cur_color], CELL)

    d.text((PANEL_X + 10, 5), "SCORE", fill=(255, 255, 255))
    d.text((PANEL_X + 10, 20), str(game.score), fill=(255, 255, 255))
    d.text((PANEL_X + 10, 45), "NEXT", fill=(255, 255, 255))

    for i, (name, color) in enumerate(game.next_queue):
        ox = PANEL_X + 50
        oy = 75 + i * 40
        for x, y in game.SHAPES[name]:
            draw_cell(d, ox + x * SMALL, oy + y * SMALL, PALETTE[color], SMALL)

    js.disp.image(img)


if __name__ == "__main__":
    from joystick import Joystick
    js = Joystick()
    game.new_game()
    for _ in range(8):
        game.step()
    draw(js)