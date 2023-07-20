from PIL import Image

b = Image.open('resources/board.png').convert("RGBA").copy()
n = Image.open('resources/ls.png').convert("RGBA").copy()

b.paste(n, (450+15, 676+15), n)
b.save('test.png')