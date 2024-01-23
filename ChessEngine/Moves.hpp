#include <string>
#include <unordered_map>

#ifndef Moves_macro
#define Moves_macro

class Move // Class to implement moves
{
    public:
        Move(std::pair<int,int>,std::pair<int,int>,std::string[8][8],int=0); //Constructor

        char pieceMoved; // Moved piece
        int startRow,startCol; // Start position of moved piece
        int endRow,endCol; // End position of moved piece
        int special; // Whether pawn promnoted, 0 for none, 1 for knight, 2 for bishop, 3 for rook, 4 for queen , 5 for right castle, 6 for left castle
        char key_to_piece[5] = {' ','N','B','R','Q'};
};

Move::Move(std::pair<int,int> start,std::pair<int,int> end,std::string board[8][8],int promote)
{
    this->pieceMoved = board[start.first][start.second][1];
    this->startRow = start.first;
    this->startCol = start.second;
    this->endRow = end.first;
    this->endCol = end.second;
    this->special = promote;
}

#endif