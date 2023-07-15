from PIL import Image
import chess.pgn as pgn #type: ignore
import io
from io import StringIO
import random
#from board_to_fen.predict import get_fen_from_image
import chess #type: ignore

coords = {
    'a8' : [-20, -20], 'b8' : [220, -20], 'c8' : [450, -20], 'd8' : [680, -20], 'e8' : [910, -20], 'f8' : [1140, -20], 'g8' : [1370, -20], 'h8' : [1600, -20],
    'a7' : [-20, 210], 'b7' : [220, 210], 'c7' : [450, 210], 'd7' : [680, 210], 'e7' : [910, 210], 'f7' : [1140, 210], 'g7' : [1370, 210], 'h7' : [1600, 210],
    'a6' : [-20, 443], 'b6' : [220, 443], 'c6' : [450, 443], 'd6' : [680, 443], 'e6' : [910, 443], 'f6' : [1140, 443], 'g6' : [1370, 443], 'h6' : [1600, 443],
    'a5' : [-20, 676], 'b5' : [220, 676], 'c5' : [450, 676], 'd5' : [680, 676], 'e5' : [910, 676], 'f5' : [1140, 676], 'g5' : [1370, 676], 'h5' : [1600, 676],
    'a4' : [-20, 909], 'b4' : [220, 909], 'c4' : [450, 909], 'd4' : [680, 909], 'e4' : [910, 909], 'f4' : [1140, 909], 'g4' : [1370, 909], 'h4' : [1600, 909],
    'a3' : [-20, 1142], 'b3' : [220, 1142], 'c3' : [450, 1142], 'd3' : [680, 1142], 'e3' : [910, 1142], 'f3' : [1140, 1142], 'g3' : [1370, 1142], 'h3' : [1600, 1142],
    'a2' : [-20, 1375], 'b2' : [220, 1375], 'c2' : [450, 1375], 'd2' : [680, 1375], 'e2' : [910, 1375], 'f2' : [1140, 1375], 'g2' : [1370, 1375], 'h2' : [1600, 1375],
    'a1' : [-20, 1608], 'b1' : [220, 1608], 'c1' : [450, 1608], 'd1' : [680, 1608], 'e1' : [910, 1608], 'f1' : [1140, 1608], 'g1' : [1370, 1608], 'h1' : [1600, 1608]
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

    board.paste(r, (-20, -20), r)
    board.paste(n, (220, -20), n)
    board.paste(b, (450, -20), b)
    board.paste(q, (680, -20), q)
    board.paste(k, (910, -20), k)
    board.paste(b, (1140, -20), b)
    board.paste(n, (1370, -20), n)
    board.paste(r, (1600, -20), r)

    board.paste(R, (-20, 1600), R)
    board.paste(N, (220, 1600), N)
    board.paste(B, (450, 1600), B)
    board.paste(Q, (680, 1600), Q)
    board.paste(K, (910, 1600), K)
    board.paste(B, (1140, 1600), B)
    board.paste(N, (1370, 1600), N)
    board.paste(R, (1600, 1600), R)

    for i in range(8):
        board.paste(p, (-20 + 233 * i, 210), p)
        board.paste(P, (-20 + 233 * i, 1370), P)

    return board

def movepiece(movefrom, moveto, b, cb):

    ismovevalid = validatemove(cb, movefrom, moveto)

    if ismovevalid == False:
        return None, None, None, None

    cb.push(chess.Move.from_uci(movefrom + moveto))

    ischeckmate = cb.is_checkmate()
    isstalemate = cb.is_stalemate()

    isover = ''

    capturedpiececoords = []

    if (getcapturedpiece(cb, str(moveto)) != 0):
        capturedpiececoords = coords[moveto.lower()]

        cpx = capturedpiececoords[0]
        cpy = capturedpiececoords[1]

        capturedpiecesq = solve(moveto)
        capturedpiecesqcolor = ''

        if capturedpiecesq == True:
            capturedpiecesqcolor = 'ls'
        else:
            capturedpiecesqcolor = 'bs'

        cpsq = Image.open('resources/' + str(capturedpiecesqcolor) + '.png').convert("RGBA").copy()
        b.paste(cpsq, (cpx, cpy), cpsq)

    cb.push_san(moveto)

    movefromcoords = coords[movefrom.lower()]
    movetocoords = coords[moveto.lower()]

    mtx = movetocoords[0]
    mty = movetocoords[1]

    mfx = movefromcoords[0]
    mfy = movefromcoords[1]

    #print(mfx, mfy)
    #print(mtx, mty)

    piece = cb.piece_at(chess.parse_square(moveto.lower()))

    originalpiecesq = solve(movefrom)
    originalpiecesqcolor = ''

    originalpiecesqcolor = 'ls' if originalpiecesq == True else 'bs'
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
    b.paste(isq, (mfx + 15, mfy + 15), isq)

    if ischeckmate == True:
        isover = 'checkmate'
        return cb, b, fen, pgn_, isover

    if isstalemate == True:
        isover = 'stalemate'
        return cb, b, fen, pgn_, isover

    return cb, b, fen, pgn_, isover

def solve(coordinate):
    return (ord(coordinate[0]))%2 != int(coordinate[1])%2
   
def validatemove(cb, movefrom, moveto):
    legal_moves = list(cb.legal_moves)
    return any(
        chess.Move.from_uci(movefrom + moveto) == legal_move
        for legal_move in legal_moves
    )
   
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

def getcapturedpiece(board, move):
    if board.is_capture(move):
        if board.is_en_passant(move):
            return chess.PAWN
        else:
            return board.piece_at(move).piece_type
    return 0

def isedgesquare(square):
    return 'true' if square in edgesquares else 'false'