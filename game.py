def print_board():
    for row in board:

        for c in row:
            if c == 0:
                print(".", end=' ')
            else:
                print("#", end=' ')

        print("")   
                
W = 10
H = 20

board = []

for _ in range(H):
    board.append([0] * W)

SHAPES = {
    "T": [(-1, 0), (0, 0), (1, 0), (0, -1)],
    "I": [(-1, 0), (0, 0), (1, 0), (2, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "S": [(0, 0), (1, 0), (-1, 1), (0, 1)],
    "Z": [(-1, 0), (0, 0), (0, 1), (1, 1)],
    "J": [(-1, -1), (-1, 0), (0, 0), (1, 0)],
    "L": [(1, -1), (-1, 0), (0, 0), (1, 0)],
}

for i in SHAPES["O"]:
    board[4 + i[1]][5 + i[0]] = 1

print_board()