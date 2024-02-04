from PIL import Image
import chess.pgn as pgn #type: ignore
import io
from io import StringIO
import random
#from board_to_fen.predict import get_fen_from_image
import chess #type: ignore

coords = {
    'a8' : [-20+15, -20+15], 'b8' : [220+15, -20+15], 'c8' : [450+15, -20+15], 'd8' : [680+15, -20+15], 'e8' : [910+15, -20+15], 'f8' : [1140+15, -20+15], 'g8' : [1370+15, -20+15], 'h8' : [1600+15, -20+15],
    'a7' : [-20+15, 210+15], 'b7' : [220+15, 210+15], 'c7' : [450+15, 210+15], 'd7' : [680+15, 210+15], 'e7' : [910+15, 210+15], 'f7' : [1140+15, 210+15], 'g7' : [1370+15, 210+15], 'h7' : [1600+15, 210+15],
    'a6' : [-20+15, 443+15], 'b6' : [220+15, 443+15], 'c6' : [450+15, 443+15], 'd6' : [680+15, 443+15], 'e6' : [910+15, 443+15], 'f6' : [1140+15, 443+15], 'g6' : [1370+15, 443+15], 'h6' : [1600+15, 443+15],
    'a5' : [-20+15, 676+15], 'b5' : [220+15, 676+15], 'c5' : [450+15, 676+15], 'd5' : [680+15, 676+15], 'e5' : [910+15, 676+15], 'f5' : [1140+15, 676+15], 'g5' : [1370+15, 676+15], 'h5' : [1600+15, 676+15],
    'a4' : [-20+15, 909+15], 'b4' : [220+15, 909+15], 'c4' : [450+15, 909+15], 'd4' : [680+15, 909+15], 'e4' : [910+15, 909+15], 'f4' : [1140+15, 909+15], 'g4' : [1370+15, 909+15], 'h4' : [1600+15, 909+15],
    'a3' : [-20+15, 1142+15], 'b3' : [220+15, 1142+15], 'c3' : [450+15, 1142+15], 'd3' : [680+15, 1142+15], 'e3' : [910+15, 1142+15], 'f3' : [1140+15, 1142+15], 'g3' : [1370+15, 1142+15], 'h3' : [1600+15, 1142+15],
    'a2' : [-20+15, 1375+15], 'b2' : [220+15, 1375+15], 'c2' : [450+15, 1375+15], 'd2' : [680+15, 1375+15], 'e2' : [910+15, 1375+15], 'f2' : [1140+15, 1375+15], 'g2' : [1370+15, 1375+15], 'h2' : [1600+15, 1375+15],
    'a1' : [-20+15, 1608+15], 'b1' : [220+15, 1608+15], 'c1' : [450+15, 1608+15], 'd1' : [680+15, 1608+15], 'e1' : [910+15, 1608+15], 'f1' : [1140+15, 1608+15], 'g1' : [1370+15, 1608+15], 'h1' : [1600+15, 1608+15]
}

edgesquares = {
    'a1': [-20, 1608], 'b1': [220, 1608], 'c1': [450, 1608], 'd1': [680, 1608], 'e1': [910, 1608], 'f1': [1140, 1608], 'g1': [1370, 1608], 'h1': [1600, 1608],
    'a2': [-20, 1375], 'a3': [-20, 1142], 'a4': [-20, 909], 'a5': [-20, 676], 'a6': [-20, 443], 'a7': [-20, 210], 'a8': [-20, -20]
}

edgesquarespath = {
    'a1': 'resources/edge_sq/a1.png', 'b1': 'resources/edge_sq/b1.png', 'c1': 'resources/edge_sq/c1.png', 'd1': 'resources/edge_sq/d1.png', 'e1': 'resources/edge_sq/e1.png', 'f1': 'resources/edge_sq/f1.png', 'g1': 'resources/edge_sq/g1.png', 'h1': 'resources/edge_sq/h1.png',
    'a2': 'resources/edge_sq/a2.png', 'a3': 'resources/edge_sq/a3.png', 'a4': 'resources/edge_sq/a4.png', 'a5': 'resources/edge_sq/a5.png', 'a6': 'resources/edge_sq/a6.png', 'a7': 'resources/edge_sq/a7.png', 'a8': 'resources/edge_sq/a8.png'
}

# is_edge_square = {
#     'a1': 'true', 'b1': 'true', 'c1': 'true', 'd1': 'true', 'e1': 'true', 'f1': 'true', 'g1': 'true', 'h1': 'true',
#     'a2': 'true', 'a3': 'true', 'a4': 'true', 'a5': 'true', 'a6': 'true', 'a7': 'true', 'a8': 'true'
# }

def createboard():
    board = Image.open('resources/board.png').convert("RGBA").copy()

    K = Image.open('resources/white/K.png').convert("RGBA").copy()
    Q = Image.open('resources/white/Q.png').convert("RGBA").copy()
    B = Image.open('resources/white/B.png').convert("RGBA").copy()
    N = Image.open('resources/white/N.png').convert("RGBA").copy()
    R = Image.open('resources/white/R.png').convert("RGBA").copy()
    P = Image.open('resources/white/P.png').convert("RGBA").copy()

    k = Image.open('resources/black/k.png').convert("RGBA").copy()
    q = Image.open('resources/black/q.png').convert("RGBA").copy()
    b = Image.open('resources/black/b.png').convert("RGBA").copy()
    n = Image.open('resources/black/n.png').convert("RGBA").copy()
    r = Image.open('resources/black/r.png').convert("RGBA").copy()
    p = Image.open('resources/black/p.png').convert("RGBA").copy()

    board.paste(r, (-20+15, -20+15), r)
    board.paste(n, (220+15, -20+15), n)
    board.paste(b, (450+15, -20+15), b)
    board.paste(q, (680+15, -20+15), q)
    board.paste(k, (910+15, -20+15), k)
    board.paste(b, (1140+15, -20+15), b)
    board.paste(n, (1370+15, -20+15), n)
    board.paste(r, (1600+15, -20+15), r)

    board.paste(R, (-20+15, 1600+15), R)
    board.paste(N, (220+15, 1600+15), N)
    board.paste(B, (450+15, 1600+15), B)
    board.paste(Q, (680+15, 1600+15), Q)
    board.paste(K, (910+15, 1600+15), K)
    board.paste(B, (1140+15, 1600+15), B)
    board.paste(N, (1370+15, 1600+15), N)
    board.paste(R, (1600+15, 1600+15), R)

    for i in range(8):
        board.paste(p, (-20 + 15 + 232 * i, 210 + 15), p)
        board.paste(P, (-20 + 15 + 232 * i, 1370 + 15), P)

    return board

def create_board_from_fen(fen):
    board = Image.open('resources/board.png').convert("RGBA").copy()

    piece_mapping = {
        'k': 'black/K.png', 'q': 'black/Q.png', 'b': 'black/B.png', 'n': 'black/N.png', 'r': 'black/R.png', 'p': 'black/P.png',
        'K': 'white/K.png', 'Q': 'white/Q.png', 'B': 'white/B.png', 'N': 'white/N.png', 'R': 'white/R.png', 'P': 'white/P.png'
    }

    row, col = 0, 0

    for char in fen:
        if char == ' ':
            break
        elif char == '/':
            row += 1
            col = 0
        elif char.isdigit():
            col += int(char)
        elif piece_image_path := piece_mapping.get(char):
            piece_image = Image.open(f'resources/{piece_image_path}').convert("RGBA").copy()
            x, y = coords[f'{chr(ord("a") + col)}{8 - row}']
            board.paste(piece_image, (x, y), piece_image)
            col += 1

    return board


def movepiece(movefrom, moveto, b, cb: chess.Board):

    ismovevalid = validatemove(cb, movefrom, moveto)

    if ismovevalid == False:
        return cb, None, None, None, None

    cb.push(chess.Move.from_uci(movefrom + moveto))

    ischeckmate = cb.is_checkmate()
    isstalemate = cb.is_stalemate()

    isover = ''

    capturedpiececoords = []

    if (getcapturedpiece(cb, movefrom, moveto)):
        _extracted_from_movepiece_18(moveto, b)
    #cb.push_san(moveto)

    movefromcoords = coords[movefrom.lower()]
    movetocoords = coords[moveto.lower()]

    mtx = movetocoords[0]
    mty = movetocoords[1]

    mfx = movefromcoords[0]
    mfy = movefromcoords[1]

    #print(mfx, mfy)
    #print(mtx, mty)

    piece = cb.piece_at(chess.parse_square(moveto.lower()))

    originalpiecesqcolor = _extracted_from_movepiece_23(movefrom)
    piece_color = ''
    piece_color = 'white' if piece.color == True else 'black'
    fen = cb.fen()
    pgn_ = fen_to_pgn(fen)

    isq = Image

    ipiece = (
        Image.open(f'resources/{piece_color}/{str(piece)}.png')
        .convert("RGBA")
        .copy()
    )

    if isedgesquare(movefrom.lower()) == 'true':
        isq = Image.open(edgesquarespath[str(movefrom.lower())]).convert("RGBA").copy()
    elif isedgesquare(movefrom.lower()) == 'false':
        isq = (
            Image.open(f'resources/{originalpiecesqcolor}.png')
            .convert("RGBA")
            .copy()
        )

    b.paste(ipiece, (mtx, mty), ipiece)
    b.paste(isq, (mfx, mfy), isq)

    if ischeckmate == True:
        isover = 'checkmate'
        return cb, b, fen, pgn_, isover

    if isstalemate == True:
        isover = 'stalemate'
        return cb, b, fen, pgn_, isover

    return cb, b, fen, pgn_, isover


# TODO Rename this here and in `movepiece`
def _extracted_from_movepiece_18(moveto, b):
    capturedpiececoords = coords[moveto.lower()]

    cpx = capturedpiececoords[0]
    cpy = capturedpiececoords[1]

    capturedpiecesqcolor = _extracted_from_movepiece_23(moveto)
    cpsq = (
        Image.open(f'resources/{capturedpiecesqcolor}.png')
        .convert("RGBA")
        .copy()
    )
    b.paste(cpsq, (cpx, cpy), cpsq)


# TODO Rename this here and in `movepiece`
def _extracted_from_movepiece_23(arg0):
    capturedpiecesq = solve(arg0)
    result = ''

    return 'ls' if capturedpiecesq == True else 'bs'

def solve(coordinate):
    return (ord(coordinate[0]))%2 != int(coordinate[1])%2
   
def validatemove(cb, movefrom, moveto):
    legal_moves = list(cb.legal_moves)

    try:
        m = chess.Move.from_uci(movefrom + moveto)
    except chess.InvalidMoveError as e:
        return False

    return m in legal_moves
   
def fen_to_pgn(fen):
    game = chess.pgn.Game.from_board(chess.Board(fen))
    pgn = game.accept(chess.pgn.StringExporter())
    return pgn

def get_moves_from_pgn(pgn):
    pgn_io = StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)
    moves = []

    board = game.board()
    for move in game.mainline_moves():
        moves.append(move.uci())
        board.push(move)

    return moves

def generateGameID():
    return random.randint(10000000, 99999999)

def image_to_byte_array(image) -> bytes:
  # BytesIO is a file-like buffer stored in memory
  imgByteArr = io.BytesIO()
  # image.save expects a file-like as a argument
  image.save(imgByteArr, format='PNG')
  # Turn the BytesIO object back into a bytes object
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

def getcapturedpiece(board, movefrom, moveto):
    move = chess.Move.from_uci(movefrom + moveto)

    if board.is_capture(move):
        return True if board.is_en_passant(move) else True
    return False

def isedgesquare(square):
    return 'true' if square in edgesquares else 'false'