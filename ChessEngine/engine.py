import numpy as np
import copy
# UNDO MOVES IS LEFT.

def find(value,l):
    for i in range(len(l)):
        for j in range(len(l[0])):
            if l[i][j] == value:
                return (i,j)
    return (0,0)

def check_equal(arr1,arr2):
    for i in range(len(arr1)):
        for j in range(len(arr1)):
            if arr1[i][j] != arr2[i][j]:
                return False
    return True

class State():
    def __init__(self): # Initializes game state
        self.board = np.array(
            [["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        )

        self.moveFunctions = {'P': self.getPawnMoves,'R':self.getRookMoves,'B':self.getBishopMoves,'N':self.getKnightMoves,'Q':self.getQueenMoves,'K':self.getKingMoves}
        self.move = True
        self.whitekingloc = self.findKing('white')
        self.blackkingloc = self.findKing('black')
        self.whiteRcastle = True
        self.whiteLcastle = True
        self.blackLcastle = True
        self.blackRcastle = True
        self.log = []
        self.positionMemory = []
        self.positionMemory.append(self.board.copy())

    def findKing(self,color): # This function returns the position of the king
        for row in range(8):
            for column in range(8):
                if color == 'white' and self.board[row][column]=='wK':
                    return (row,column)
                elif color == 'black' and self.board[row][column]=='bK':
                    return (row,column)
        print('Bad position')



    def makeMove(self,move): # Driver function to make a move, also handles castling logic.
        # Castle king check
        if self.board[move.startRow][move.startCol] == 'wK' and move.startRow == 7 and move.startCol == 4:
            self.whiteLcastle = False
            self.whiteRcastle = False
            if move.endCol == 6:
                self.board[7][7] = '--'
                self.board[7][5] = 'wR'
            if move.endCol == 2:
                self.board[7][0] = '--'
                self.board[7][3] = 'wR'

        elif self.board[move.startRow][move.startCol] == 'bK' and move.startRow == 0 and move.startCol == 4:
            self.blackLcastle = False
            self.blackRcastle = False
            if move.endCol == 6:
                self.board[0][7] = '--'
                self.board[0][5] = 'bR'
            if move.endCol == 2:
                self.board[0][0] = '--'
                self.board[0][3] = 'bR'

        # Castle rook check
        if self.board[move.startRow][move.startCol] == 'wR':
            if move.startCol == 7 and move.startRow == 7:
                self.whiteRcastle = False
            elif move.startCol == 0 and move.startRow == 7:
                self.whiteLcastle = False
        elif self.board[move.startRow][move.startCol] == 'bR':
            if move.startCol == 7 and move.startRow == 0:
                self.blackRcastle = False
            elif move.startCol == 0 and move.startRow == 0:
                self.blackLcastle = False

        # En Passant check.
        if self.board[move.startRow][move.startCol][1] == 'P':
            if move.startCol != move.endCol and self.board[move.endRow][move.endCol] == '--':
                # This condition is where en passant happens
                row_change = -1 if self.move else 1
                self.board[move.endRow-row_change][move.endCol] = '--'
        
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.moved
        self.log.append(move)
        
        self.move = not self.move
        self.positionMemory.append(self.board.copy())

        if move.moved == 'wK':
            self.whitekingloc = (move.endRow,move.endCol)
        elif move.moved == 'bK':
            self.blackkingloc = (move.endRow,move.endCol)

    def checkThreefold(self): # Checks for threefold repetition
        currentPos = self.board
        count = 0
        for position in self.positionMemory:
            if (position == currentPos).all():
                count+=1
        if count >= 3:
            return True
        return False
    
    def is_promote(self): # Checks promotion
        move = self.log[-1]
        if move.moved[1] == 'P':
            req_row = 7 if self.move else 0
            if move.endRow == req_row:
                return True
        return False
    
    def promote(self): # Promotes
        move = self.log[-1]
        convert = {1:'N',2:'B',3:'R',4:'Q',0:'--'}
        self.board[move.endRow][move.endCol] = move.moved[0]+convert[move.promote]
        
    def undoMove(self): # This function undoes a move, not complete.
        if len(self.log) != 0:
            move = self.log.pop()
            self.board[move.startRow][move.startCol] = move.moved
            self.board[move.endRow][move.endCol] = move.to
            self.move = not self.move

    def isCheck(self,board): # This function checks if the current game state is in check
        if self.move:
            turn = 'w'
            opp = 'b'
        else:
            turn = 'b'
            opp = 'w'
        pos = find(turn+'K',board)
        directions = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,-1),(-1,1),(1,-1)]

        # Checking for queen, rook and bishop
        count = 0
        for direction in directions:
            temp_row = pos[0]
            temp_col = pos[1]
            while temp_row+direction[0]<8 and temp_row+direction[0]>=0 and temp_col+direction[1]>=0 and temp_col+direction[1]<8:
                temp_row += direction[0]
                temp_col += direction[1]
                if count < 4:
                    if board[temp_row][temp_col] == opp+'Q' or board[temp_row][temp_col] == opp+'R':
                        return True
                    if board[temp_row][temp_col] != '--':
                        break
                if count >= 4:
                    if board[temp_row][temp_col] == opp+'Q' or board[temp_row][temp_col] == opp+'B':
                        return True
                    if board[temp_row][temp_col] != '--':
                        break
            count += 1

        # Checking for king
        for direction in directions:
            temp_row = pos[0]
            temp_col = pos[1]
            if temp_row+direction[0]<8 and temp_row+direction[0]>=0 and temp_col+direction[1]>=0 and temp_col+direction[1]<8:
                temp_row += direction[0]
                temp_col += direction[1]
                if board[temp_row][temp_col] == opp+'K':
                    return True

        # Checking for knight
        directions = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for direction in directions:
            temp_row = pos[0]
            temp_col = pos[1]
            if temp_row+direction[0]<8 and temp_row+direction[0]>=0 and temp_col+direction[1]>=0 and temp_col+direction[1]<8:
                temp_row += direction[0]
                temp_col += direction[1]
                if board[temp_row][temp_col] == opp+'N':
                    return True
        
        # Checking for pawn
        row = -1 if opp == 'b' else 1
        directions = [(row,1),(row,-1)]
        for direction in directions:
            temp_row = pos[0]
            temp_col = pos[1]
            if temp_row+direction[0]<8 and temp_row+direction[0]>=0 and temp_col+direction[1]>=0 and temp_col+direction[1]<8:
                temp_row += direction[0]
                temp_col += direction[1]
                if board[temp_row][temp_col] == opp+'P':
                    return True
        return False

    def check_move(self,move): # Creates temporary game states for all possible moves to check for checks(ironic)
        board_copy = self.board.copy()
        
        # Castle check
        if board_copy[move.startRow][move.startCol] == 'wK' and move.startRow == 7 and move.startCol == 4:
            if move.endCol == 6:
                board_copy[7][7] = '--'
                board_copy[7][5] = 'wR'
            if move.endCol == 2:
                board_copy[7][0] = '--'
                board_copy[7][3] = 'wR'

        elif board_copy[move.startRow][move.startCol] == 'bK' and move.startRow == 0 and move.startCol == 4:
            if move.endCol == 6:
                board_copy[0][7] = '--'
                board_copy[0][5] = 'bR'
            if move.endCol == 2:
                board_copy[0][0] = '--'
                board_copy[0][3] = 'bR'

        # En passant check
        if board_copy[move.startRow][move.startCol][1] == 'P':
            if move.startCol != move.endCol and board_copy[move.endRow][move.endCol] == '--':
                # This condition is where en passant happens
                row_change = -1 if self.move else 1
                board_copy[move.endRow-row_change][move.endCol] = '--'

        board_copy[move.startRow][move.startCol] = '--'
        board_copy[move.endRow][move.endCol] = move.moved
        return self.isCheck(board_copy)

    def getValidMove(self): # Removes invalid moves from all possible moves
        possible = self.getPossibleMoves()
        self.moves = []
        for possible_move in possible:
            checker = self.check_move(possible_move)
            if not checker:
                self.moves.append(possible_move)
        return self.moves

    def getPossibleMoves(self): # Generates moves based on each piece
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.move) or (turn == 'b' and not self.move):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves

    def getPawnMoves(self,r,c,moves): # Pawn movement logic, needs en passant and promotion logic
        if self.move:
            if self.board[r-1][c] == '--':
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == '--':
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c-1),self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
        else:
            if self.board[r+1][c] == '--':
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == '--':
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c-1),self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))
        if len(self.log) > 0:
            lastMove = self.log[-1]
            req_row = 1 if self.move else 6
            if lastMove.startRow == req_row and lastMove.endRow == r and abs(lastMove.endCol - c) == 1:
                row_change = -1 if self.move else 1
                moves.append(Move((r,c),(r+row_change,c + (lastMove.endCol - c)),self.board))

    def getRookMoves(self,r,c,moves): # Rook movement logic
        dir = [(0,1),(1,0),(0,-1),(-1,0)]
        for i in dir:
            temp_r = r
            temp_c = c
            while temp_r+i[0] <= 7 and temp_r+i[0] >= 0 and temp_c+i[1]<=7 and temp_c+i[1]>=0:
                if self.board[temp_r+i[0]][temp_c+i[1]] == '--':
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    temp_r += i[0]
                    temp_c += i[1]
                elif (self.board[temp_r+i[0]][temp_c+i[1]][0] == 'b' and self.move) or ( self.board[temp_r+i[0]][temp_c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    break
                else:
                    break
    
    def getBishopMoves(self,r,c,moves): # Bishop movement logic
        dir = [(1,1),(-1,-1),(1,-1),(-1,1)]
        for i in dir:
            temp_r = r
            temp_c = c
            while temp_r+i[0] <= 7 and temp_r+i[0] >= 0 and temp_c+i[1]<=7 and temp_c+i[1]>=0:
                if self.board[temp_r+i[0]][temp_c+i[1]] == '--':
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    temp_r += i[0]
                    temp_c += i[1]
                elif (self.board[temp_r+i[0]][temp_c+i[1]][0] == 'b' and self.move) or ( self.board[temp_r+i[0]][temp_c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    break
                else:
                    break

    def getKnightMoves(self,r,c,moves): # Knight movement logic
        dir = [(2,1),(2,-1),(1,2),(1,-2),(-1,-2),(-1,2),(-2,-1),(-2,1)]
        for i in dir:
            if r+i[0] <= 7 and r+i[0] >= 0 and c+i[1] <= 7 and c+i[1] >=0:
                if self.board[r+i[0]][c+i[1]] == '--':
                    moves.append(Move((r,c),(r+i[0],c+i[1]),self.board))
                elif (self.board[r+i[0]][c+i[1]][0] == 'b' and self.move) or ( self.board[r+i[0]][c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(r+i[0],c+i[1]),self.board))

    def getQueenMoves(self,r,c,moves): # Queen movement logic
        dir = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]
        for i in dir:
            temp_r = r
            temp_c = c
            while temp_r+i[0] <= 7 and temp_r+i[0] >= 0 and temp_c+i[1]<=7 and temp_c+i[1]>=0:
                if self.board[temp_r+i[0]][temp_c+i[1]] == '--':
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    temp_r += i[0]
                    temp_c += i[1]
                elif (self.board[temp_r+i[0]][temp_c+i[1]][0] == 'b' and self.move) or ( self.board[temp_r+i[0]][temp_c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    break
                else:
                    break

    def getKingMoves(self,r,c,moves): # King movement logic
        dir = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]
        for i in dir:
            if r+i[0] <= 7 and r+i[0] >= 0 and c+i[1] <= 7 and c+i[1] >=0:
                if self.board[r+i[0]][c+i[1]] == '--':
                    moves.append(Move((r,c),(r+i[0],c+i[1]),self.board))
                elif (self.board[r+i[0]][c+i[1]][0] == 'b' and self.move) or ( self.board[r+i[0]][c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(r+i[0],c+i[1]),self.board))
        if self.board[7][5] == '--' and self.board[7][6] == '--' and self.whiteRcastle and c<6:
            moves.append(Move((r,c),(r,c+2),self.board))
        if self.board[7][3] == '--' and self.board[7][2]=='--' and self.board[7][1] == '--' and self.whiteLcastle and c>=2:
            moves.append(Move((r,c),(r,c-2),self.board))
        if self.board[0][5] == '--' and self.board[0][6] == '--' and self.blackRcastle and c<6:
            moves.append(Move((r,c),(r,c+2),self.board))
        if self.board[0][3] == '--' and self.board[0][2]=='--' and self.board[0][1] == '--' and self.blackLcastle and c>=2:
            moves.append(Move((r,c),(r,c-2),self.board))    

    def getMoves(self,r,c): # Helper function to display moves
        self.display = []
        for value in self.moves:
            if value.startRow == r and value.startCol == c:
                self.display.append((value.endRow,value.endCol))
        return self.display

class Move():
    rank2row = {'1':7,'2':6,'3':5,'4':4,'5':3,'6':2,'7':1,'8':0}
    row2rank = {v:k for k,v in rank2row.items()}
    file2col = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
    col2file = {v:k for k,v in file2col.items()}

    def __init__(self,start,end,board):
        self.startRow = start[0] 
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.moved = board[self.startRow][self.startCol]
        self.to = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.promote = 0 # 0 for no promotion, 1 for knight, 2 for bishop, 3 for rook, 4 for queen

    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False

    def getNotation(self):
        piece = '' if self.moved[1] == 'P' else self.moved[1]
        return piece + self.getrankfile(self.endRow,self.endCol)
    
    def getrankfile(self,r,c):
        return self.col2file[c] + self.row2rank[r]
    

class Engine():
    def __init__(self,version=0,play=True,depth=10):
        self.play = True
        self.depth = depth
        self.moveFunctions = {'P': self.getPawnMoves,'R':self.getRookMoves,'B':self.getBishopMoves,'N':self.getKnightMoves,'Q':self.getQueenMoves,'K':self.getKingMoves}

    # Change all these to take a parameter
    def getPawnMoves(self,r,c,moves): # Pawn movement logic, needs en passant and promotion logic
        if self.move:
            if self.board[r-1][c] == '--':
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == '--':
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c-1),self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
        else:
            if self.board[r+1][c] == '--':
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == '--':
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c-1),self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))
        if len(self.log) > 0:
            lastMove = self.log[-1]
            req_row = 1 if self.move else 6
            if lastMove.startRow == req_row and lastMove.endRow == r and abs(lastMove.endCol - c) == 1:
                row_change = -1 if self.move else 1
                moves.append(Move((r,c),(r+row_change,c + (lastMove.endCol - c)),self.board))

    def getRookMoves(self,r,c,moves): # Rook movement logic
        dir = [(0,1),(1,0),(0,-1),(-1,0)]
        for i in dir:
            temp_r = r
            temp_c = c
            while temp_r+i[0] <= 7 and temp_r+i[0] >= 0 and temp_c+i[1]<=7 and temp_c+i[1]>=0:
                if self.board[temp_r+i[0]][temp_c+i[1]] == '--':
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    temp_r += i[0]
                    temp_c += i[1]
                elif (self.board[temp_r+i[0]][temp_c+i[1]][0] == 'b' and self.move) or ( self.board[temp_r+i[0]][temp_c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    break
                else:
                    break
    
    def getBishopMoves(self,r,c,moves): # Bishop movement logic
        dir = [(1,1),(-1,-1),(1,-1),(-1,1)]
        for i in dir:
            temp_r = r
            temp_c = c
            while temp_r+i[0] <= 7 and temp_r+i[0] >= 0 and temp_c+i[1]<=7 and temp_c+i[1]>=0:
                if self.board[temp_r+i[0]][temp_c+i[1]] == '--':
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    temp_r += i[0]
                    temp_c += i[1]
                elif (self.board[temp_r+i[0]][temp_c+i[1]][0] == 'b' and self.move) or ( self.board[temp_r+i[0]][temp_c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    break
                else:
                    break

    def getKnightMoves(self,r,c,moves): # Knight movement logic
        dir = [(2,1),(2,-1),(1,2),(1,-2),(-1,-2),(-1,2),(-2,-1),(-2,1)]
        for i in dir:
            if r+i[0] <= 7 and r+i[0] >= 0 and c+i[1] <= 7 and c+i[1] >=0:
                if self.board[r+i[0]][c+i[1]] == '--':
                    moves.append(Move((r,c),(r+i[0],c+i[1]),self.board))
                elif (self.board[r+i[0]][c+i[1]][0] == 'b' and self.move) or ( self.board[r+i[0]][c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(r+i[0],c+i[1]),self.board))

    def getQueenMoves(self,r,c,moves): # Queen movement logic
        dir = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]
        for i in dir:
            temp_r = r
            temp_c = c
            while temp_r+i[0] <= 7 and temp_r+i[0] >= 0 and temp_c+i[1]<=7 and temp_c+i[1]>=0:
                if self.board[temp_r+i[0]][temp_c+i[1]] == '--':
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    temp_r += i[0]
                    temp_c += i[1]
                elif (self.board[temp_r+i[0]][temp_c+i[1]][0] == 'b' and self.move) or ( self.board[temp_r+i[0]][temp_c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(temp_r+i[0],temp_c+i[1]),self.board))
                    break
                else:
                    break

    def getKingMoves(self,r,c,moves): # King movement logic
        dir = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]
        for i in dir:
            if r+i[0] <= 7 and r+i[0] >= 0 and c+i[1] <= 7 and c+i[1] >=0:
                if self.board[r+i[0]][c+i[1]] == '--':
                    moves.append(Move((r,c),(r+i[0],c+i[1]),self.board))
                elif (self.board[r+i[0]][c+i[1]][0] == 'b' and self.move) or ( self.board[r+i[0]][c+i[1]][0] == 'w' and not self.move ):
                    moves.append(Move((r,c),(r+i[0],c+i[1]),self.board))
        if self.board[7][5] == '--' and self.board[7][6] == '--' and self.whiteRcastle and c<6:
            moves.append(Move((r,c),(r,c+2),self.board))
        if self.board[7][3] == '--' and self.board[7][2]=='--' and self.board[7][1] == '--' and self.whiteLcastle and c>=2:
            moves.append(Move((r,c),(r,c-2),self.board))
        if self.board[0][5] == '--' and self.board[0][6] == '--' and self.blackRcastle and c<6:
            moves.append(Move((r,c),(r,c+2),self.board))
        if self.board[0][3] == '--' and self.board[0][2]=='--' and self.board[0][1] == '--' and self.blackLcastle and c>=2:
            moves.append(Move((r,c),(r,c-2),self.board))    

    def promoter(self,possible_moves):
        moves_with_promotion = []
        for move in possible_moves:
            if move.moved[1] != 'P':
                moves_with_promotion.append(move)
            else:
                req_row = 0 if move.moved[0] == 'w' else 7
                if move.endRow == req_row:
                    for promote in range(1,5):
                        temp_move = copy.copy(move)
                        temp_move.promote = promote
                        moves_with_promotion.append(temp_move)
                else:
                    moves_with_promotion.append(move)
        return moves_with_promotion
    
    def isCheck(self,board): # This function checks if the current game state is in check
        if self.move:
            turn = 'w'
            opp = 'b'
        else:
            turn = 'b'
            opp = 'w'
        pos = find(turn+'K',board)
        directions = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,-1),(-1,1),(1,-1)]

        # Checking for queen, rook and bishop
        count = 0
        for direction in directions:
            temp_row = pos[0]
            temp_col = pos[1]
            while temp_row+direction[0]<8 and temp_row+direction[0]>=0 and temp_col+direction[1]>=0 and temp_col+direction[1]<8:
                temp_row += direction[0]
                temp_col += direction[1]
                if count < 4:
                    if board[temp_row][temp_col] == opp+'Q' or board[temp_row][temp_col] == opp+'R':
                        return True
                    if board[temp_row][temp_col] != '--':
                        break
                if count >= 4:
                    if board[temp_row][temp_col] == opp+'Q' or board[temp_row][temp_col] == opp+'B':
                        return True
                    if board[temp_row][temp_col] != '--':
                        break
            count += 1

        # Checking for king
        for direction in directions:
            temp_row = pos[0]
            temp_col = pos[1]
            if temp_row+direction[0]<8 and temp_row+direction[0]>=0 and temp_col+direction[1]>=0 and temp_col+direction[1]<8:
                temp_row += direction[0]
                temp_col += direction[1]
                if board[temp_row][temp_col] == opp+'K':
                    return True

        # Checking for knight
        directions = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for direction in directions:
            temp_row = pos[0]
            temp_col = pos[1]
            if temp_row+direction[0]<8 and temp_row+direction[0]>=0 and temp_col+direction[1]>=0 and temp_col+direction[1]<8:
                temp_row += direction[0]
                temp_col += direction[1]
                if board[temp_row][temp_col] == opp+'N':
                    return True
        
        # Checking for pawn
        row = -1 if opp == 'b' else 1
        directions = [(row,1),(row,-1)]
        for direction in directions:
            temp_row = pos[0]
            temp_col = pos[1]
            if temp_row+direction[0]<8 and temp_row+direction[0]>=0 and temp_col+direction[1]>=0 and temp_col+direction[1]<8:
                temp_row += direction[0]
                temp_col += direction[1]
                if board[temp_row][temp_col] == opp+'P':
                    return True
        return False

    def check_move(self,move): # Creates temporary game states for all possible moves to check for checks(ironic)
        board_copy = self.board.copy()
        
        # Castle check
        if board_copy[move.startRow][move.startCol] == 'wK' and move.startRow == 7 and move.startCol == 4:
            if move.endCol == 6:
                board_copy[7][7] = '--'
                board_copy[7][5] = 'wR'
            if move.endCol == 2:
                board_copy[7][0] = '--'
                board_copy[7][3] = 'wR'

        elif board_copy[move.startRow][move.startCol] == 'bK' and move.startRow == 0 and move.startCol == 4:
            if move.endCol == 6:
                board_copy[0][7] = '--'
                board_copy[0][5] = 'bR'
            if move.endCol == 2:
                board_copy[0][0] = '--'
                board_copy[0][3] = 'bR'

        # En passant check
        if board_copy[move.startRow][move.startCol][1] == 'P':
            if move.startCol != move.endCol and board_copy[move.endRow][move.endCol] == '--':
                # This condition is where en passant happens
                row_change = -1 if self.move else 1
                board_copy[move.endRow-row_change][move.endCol] = '--'

        board_copy[move.startRow][move.startCol] = '--'
        board_copy[move.endRow][move.endCol] = move.moved
        return self.isCheck(board_copy)
    
    def getValidMove(self): # Removes invalid moves from all possible moves
        possible = self.getPossibleMoves()
        self.moves = []
        for possible_move in possible:
            checker = self.check_move(possible_move)
            if not checker:
                self.moves.append(possible_move)
        return self.moves

    def getPossibleMoves(self,board): # Generates moves based on each piece
        moves = []
        for r in range(len(board)):
            for c in range(len(board[r])):
                turn = [r][c][0]
                if (turn == 'w' and self.play) or (turn == 'b' and not self.play):
                    piece = board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves

    
    def possible_positions(self,position,possible_moves,root,depth):
        if depth == self.depth:
            return
        variations = []
        for move in possible_moves:   
            board_copy = position.copy()
            # Castle check
            if board_copy[move.startRow][move.startCol] == 'wK' and move.startRow == 7 and move.startCol == 4:
                if move.endCol == 6:
                    board_copy[7][7] = '--'
                    board_copy[7][5] = 'wR'
                if move.endCol == 2:
                    board_copy[7][0] = '--'
                    board_copy[7][3] = 'wR'

            elif board_copy[move.startRow][move.startCol] == 'bK' and move.startRow == 0 and move.startCol == 4:
                if move.endCol == 6:
                    board_copy[0][7] = '--'
                    board_copy[0][5] = 'bR'
                if move.endCol == 2:
                    board_copy[0][0] = '--'
                    board_copy[0][3] = 'bR'

            # En passant check
            if board_copy[move.startRow][move.startCol][1] == 'P':
                if move.startCol != move.endCol and board_copy[move.endRow][move.endCol] == '--':
                    # This condition is where en passant happens
                    row_change = -1 if move.moved[0] == 'w' else 1
                    board_copy[move.endRow-row_change][move.endCol] = '--'

            board_copy[move.startRow][move.startCol] = '--'
            if move.promote == 0:
                board_copy[move.endRow][move.endCol] = move.moved
            else:
                convert = {1:'N',2:'B',3:'R',4:'Q',0:'--'}
                board_copy[move.endRow][move.endCol] = move.moved[0]+convert[move.promote]
            variations.append(board_copy)
        
        root.addChildren(variations)

        for subtree in root.children:
            self.possible_positions(subtree.value)

    def evaluate_position(self,gs):
        self.position = gs.board.copy()
        possible_moves = self.promoter(gs.getValidMove())
        self.tree = TreeNode()
        self.possible_positions(position,possible_moves)



    # def evaluate(self):
    #     # Adding a very high weight to checkmate
    #     self.checkmate_weight = 10000
    #     # Defining individual piece material values
    #     self.weights = {'Q':100,'R':40,'B':25,'K':20,'P':6,'-':0}
    #     # Defining dynamic positional values
    #     self.overall_space_value = 0
    #     self.individual_piece_space_value = 0
    #     self.king_safety_value = 0

    #     self.evaluation = 0

    #     for row in self.board:
    #         for value in row:
    #             score = self.weights[value[1]]
    #             if value[0] == 'w':
    #                 self.evaluation += score
    #             if value[0] == 'b':
    #                 self.evaluation -= score

class TreeNode(): # Helper class tree implementation
    def __init__(self,position):
        self.value = position
        self.children = []

    def addChildren(self,list_of_positions):
        for position in list_of_positions:
            self.children.append(TreeNode(position))

    def isleaf(self):
        if len(self.children) == 0:
            return True
        return False

def printTree(node): # Prints a tree
    print(node.parent)
    if len(node.children) == 0:
        return
    for subtree in node.children:
        printTree(subtree)

def create_tree(root,depth):
    if depth == 8:
        return
    generated_positions = np.random.rand(5)
    root.addChildren(generated_positions)
    for subtree in root.children:
        create_tree(subtree,depth+1)