import pygame as p
import engine
import sys

width = 512
height = 512

dim = 8
sq_size = (height//dim,height//dim)
fps = 30

image = {}

def load_image():
    image['bR'] = p.transform.scale(p.image.load('images/bR.png'),sq_size)
    image['bB'] = p.transform.scale(p.image.load('images/bB.png'),sq_size)
    image['bN'] = p.transform.scale(p.image.load('images/bN.png'),sq_size)
    image['bQ'] = p.transform.scale(p.image.load('images/bQ.png'),sq_size)
    image['bK'] = p.transform.scale(p.image.load('images/bK.png'),sq_size)
    image['bP'] = p.transform.scale(p.image.load('images/bp.png'),sq_size)
    image['wR'] = p.transform.scale(p.image.load('images/wR.png'),sq_size)
    image['wB'] = p.transform.scale(p.image.load('images/wB.png'),sq_size)
    image['wN'] = p.transform.scale(p.image.load('images/wN.png'),sq_size)
    image['wQ'] = p.transform.scale(p.image.load('images/wQ.png'),sq_size)
    image['wK'] = p.transform.scale(p.image.load('images/wK.png'),sq_size)
    image['wP'] = p.transform.scale(p.image.load('images/wp.png'),sq_size)

def drawBoard(screen):
    colors = [p.Color("white"),p.Color("gray")]
    for i in range(dim):
        for j in range(dim):
            color = colors[((i+j)%2)]
            p.draw.rect(screen,color,p.Rect(j*sq_size[0], i*sq_size[0], sq_size[0], sq_size[0]))

def drawPieces(screen,gs):
    for i in range(dim):
        for j in range(dim):
            piece = gs.board[i][j]
            if piece != '--':
                screen.blit(image[piece],p.Rect(j*sq_size[0], i*sq_size[0], sq_size[0], sq_size[0]))

def drawHighlight(screen):
    loc = p.mouse.get_pos()
    col = loc[0]//sq_size[0]
    row = loc[1]//sq_size[0]
    p.draw.rect(screen,p.Color('yellow'),p.Rect(col*sq_size[0], row*sq_size[0], sq_size[0], sq_size[0]))

def drawSelected(screen,selected):
    if selected != ():
        p.draw.rect(screen,p.Color('yellow'),p.Rect(selected[1]*sq_size[0], selected[0]*sq_size[0], sq_size[0], sq_size[0]))
def drawPossible(screen,selected):
    if selected != ():
        p.draw.circle(screen,p.Color('dark gray'),(selected[1]*sq_size[0]+2+sq_size[0]//2, selected[0]*sq_size[0]+sq_size[0]//2), sq_size[0]//10)

def drawGameState(screen,gs,clicks):
    drawBoard(screen)
    # drawHighlight(screen)
    for selected in clicks:
        drawSelected(screen,selected)
    drawPieces(screen,gs)
    if len(clicks) == 1:
        possible = gs.getMoves(clicks[0][0],clicks[0][1])
        for pos in possible:
            drawPossible(screen,pos)
    

def main():
    p.init()
    screen = p.display.set_mode((width,height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.State()
    load_image()
    running = True
    selected = ()
    clicks = []
    prev = []
    validMoves = gs.getValidMove()
    moveMade = False
    isWait = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            if isWait:
                if e.type == p.KEYDOWN:
                    if e.key == p.K_n:
                        gs.log[-1].promote = 1
                        isWait = False
                        gs.promote()
                    elif e.key == p.K_b:
                        gs.log[-1].promote = 2
                        isWait = False
                        gs.promote()
                    elif e.key == p.K_r:
                        gs.log[-1].promote = 3
                        isWait = False
                        gs.promote()
                    elif e.key == p.K_q:
                        gs.log[-1].promote = 4
                        isWait = False
                        gs.promote()
            else:
                if e.type == p.MOUSEBUTTONDOWN:
                    loc = p.mouse.get_pos()
                    col = loc[0]//sq_size[0]
                    row = loc[1]//sq_size[0]
                    if selected == (row,col):
                        selected = ()
                        clicks = []
                        prev = []
                    elif (len(clicks) == 0 and gs.board[row][col] != "--") or (len(clicks) != 0):
                        selected = (row,col)
                        clicks.append(selected)
                        prev = clicks
                    if len(clicks) == 2:
                        move = engine.Move(clicks[0],clicks[1],gs.board)
                        if move in validMoves:
                            gs.makeMove(move)
                            if gs.is_promote():
                                isWait = True
                            moveMade = True
                        else:
                            prev = []
                            selected = ()
                        clicks=[]
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z:
                        gs.undoMove()
                        moveMade = True
                        selected = ()
                        clicks=[]
                        prev = []

        if isWait:
            drawGameState(screen,gs,prev)
            clock.tick(fps)
            p.display.flip()
            continue
        drawGameState(screen,gs,prev)
        clock.tick(fps)
        p.display.flip()
        if moveMade:
            validMoves = gs.getValidMove()
            if len(validMoves) == 0:
                if gs.isCheck(gs.board):
                    print('Checkmate!')
                else:
                    print('Stalemate!')    
                break
            if gs.checkThreefold():
                print('stalemate')
                break
            moveMade = False
main()