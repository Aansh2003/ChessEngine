#include <string>
#include <iostream>
#include <vector>
#include <unordered_map>
#include <functional>
#include "Moves.hpp"
#include "engineTree.hpp"
#include<cmath>
#include<queue>
#include<stack>

using func = std::function<void(std::string[8][8],std::pair<int,int>,bool,std::vector<Move>&,bool,bool,bool,bool)>;

struct Board{
    std::string board[8][8];
};

class Engine
{
    public:
        Engine(int=10,int=10); // Constructor
        void evaluate(std::string[8][8],bool,bool,bool,bool,bool);

        static void PawnMoves(std::string[8][8],std::pair<int,int>,bool,std::vector<Move>&,bool,bool,bool,bool); // Pawn move logic
        static void KnightMoves(std::string[8][8],std::pair<int,int>,bool,std::vector<Move>&,bool,bool,bool,bool); // Knight move logic
        static void BishopMoves(std::string[8][8],std::pair<int,int>,bool,std::vector<Move>&,bool,bool,bool,bool); // Bishop move logic
        static void RookMoves(std::string[8][8],std::pair<int,int>,bool,std::vector<Move>&,bool,bool,bool,bool); // Rook move logic
        static void QueenMoves(std::string[8][8],std::pair<int,int>,bool,std::vector<Move>&,bool,bool,bool,bool); // Queen move logic
        static void KingMoves(std::string[8][8],std::pair<int,int>,bool,std::vector<Move>&,bool,bool,bool,bool); // King move logic
        static bool isCheck(std::string[8][8],bool); // Checks if position is in check
        struct Board executeMove(std::string[8][8],Move);
        std::vector<Move> generateMoves(std::string[8][8],bool,bool,bool,bool,bool);
        void createGameTree(TreeNode* tree,std::string[8][8],bool,bool,bool,bool,bool,int,Move*);
        void createGameTree(TreeNode*&,std::string[8][8],bool,bool,bool,bool,bool);
        std::unordered_map<char, func> function_lookup; // Function maps to piece
        std::unordered_map<std::string,float> value_table;
        static float evaluate(TreeNode*,std::unordered_map<std::string,float>);

    private:
        static bool inBoard(int,int); // Helper function to check if row and col in board limits
        static std::pair<int,int> findKing(std::string[8][8],bool);

        int depth; // How deep engine thinks
        int type; // Type of logic
        bool wLCastle,wRCastle,bLCastle,bRCastle;
};

Engine::Engine(int depth,int type)
{
    this->depth = depth*2;
    this->type = type;
    function_lookup['P'] = PawnMoves;
    function_lookup['N'] = KnightMoves;
    function_lookup['B'] = BishopMoves;
    function_lookup['R'] = RookMoves;
    function_lookup['Q'] = QueenMoves;
    function_lookup['K'] = KingMoves;

    value_table["wQ"] = 9;
    value_table["wR"] = 5;
    value_table["wB"] = 3;
    value_table["wN"] = 3;
    value_table["wP"] = 1;
    value_table["bQ"] = -9;
    value_table["bR"] = -5;
    value_table["bB"] = -3;
    value_table["bN"] = -3;
    value_table["bP"] = -1;
    value_table["--"] = 0;
}

float Engine::evaluate(TreeNode* tree,std::unordered_map<std::string,float> value_table)
{
    float score = 0;

    for(int i=0;i<8;i++)
    {
        for(int j=0;j<8;j++)
        {
            score += value_table[tree->board[i][j]];
        }
    }
    return score;
}

void Engine::createGameTree(TreeNode*& tree, std::string board[8][8],bool whiteToPlay, bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle)
{
    tree = new TreeNode(board,whiteToPlay,wRCastle,wLCastle,bRCastle,bLCastle,0,NULL);
    std::stack<TreeNode*> tree_queue;
    tree_queue.push(tree);
    int count=0;
    while(tree_queue.size()!=0)
    {
        TreeNode* current = tree_queue.top();
        tree_queue.pop();
        if(current->parent!=NULL)
        {
            current->parent->AddChild(current);
        }

        bool current_turn = current->whiteToPlay;
        bool curr_wRC = current->wRCastle;
        bool curr_wLC = current->wLCastle;
        bool curr_bRC = current->bRCastle;
        bool curr_bLC = current->bLCastle;
        int curr_depth = current->depth;
        Move* prevMove = current->prev;

        if(curr_depth == depth-1)
        {
            current->evaluation = evaluate(current,value_table);
            TreeNode::pruneTree(tree,whiteToPlay);
            continue;
        }

        std::string current_board[8][8];
        for(int i=0;i<8;i++)
        {
            for(int j=0;j<8;j++)
            {
                current_board[i][j] = current->board[i][j];
            }
        }

        std::vector<Move> possible_moves = generateMoves(current_board,current_turn,curr_wLC,curr_wRC,curr_bLC, curr_bRC);

        // Handling en passant
        if(prevMove != NULL)
        {
            if(prevMove->pieceMoved=='P')
            {
                if(abs(prevMove->endRow-prevMove->startRow)==2)
                {
                    char side = current_board[prevMove->endRow][prevMove->endCol][0];
                    std::string opp;
                    int dir;
                    if(side=='w')
                    {
                        opp = "bP";
                        dir = 1;
                    }
                    else
                    {
                        opp = "wP";
                        dir = -1;
                    }
                    if(inBoard(prevMove->endRow,prevMove->endCol+1) and current_board[prevMove->endRow][prevMove->endCol+1]==opp)
                    {
                        possible_moves.push_back(Move(std::make_pair(prevMove->endRow,prevMove->endCol+1),std::make_pair(prevMove->endRow+dir,prevMove->endCol),board));
                    }
                    if(inBoard(prevMove->endRow,prevMove->endCol-1) and current_board[prevMove->endRow][prevMove->endCol-1]==opp)
                    {
                        possible_moves.push_back(Move(std::make_pair(prevMove->endRow,prevMove->endCol-1),std::make_pair(prevMove->endRow+dir,prevMove->endCol),board));
                    }
                }
            }
        }
        if(possible_moves.size()==0)
        {
            if(isCheck(current_board,current_turn))
            {
                if(current_turn)
                {
                    current->evaluation = -10000;
                }
                else
                {
                    current->evaluation = 10000;
                }
            }
            else
                current->evaluation = 0;
            TreeNode::pruneTree(tree,whiteToPlay);
        }
        //Handles castling memory
        for(Move move:possible_moves)
        {
            if(move.pieceMoved == 'K')
            {
                if(current_turn)
                {
                    curr_wRC = false;
                    curr_wLC = false;
                }
                else
                {
                    curr_bRC = false;
                    curr_bLC = false;
                }
            }
            if(move.pieceMoved == 'R')
            {
                if(current_turn)
                {
                    if(move.startCol==0)
                        curr_wLC = false;
                    else
                        curr_wRC = false;
                }
                else
                {
                    if(move.startCol==0)
                        curr_bLC = false;
                    else
                        curr_bRC = false;
                }
            }
            Board b = executeMove(current_board,move);
            TreeNode* child = new TreeNode(b.board,!current_turn,curr_wRC,curr_wLC,curr_bRC,curr_bLC,curr_depth+1,&move,current);
            if(current->depth == this->depth)
            {
                continue;
            }
            tree_queue.push(child);
        }
    }
}

void Engine::createGameTree(TreeNode* tree,std::string board[8][8],bool whiteToPlay, bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle,int depth,Move* prevMove)
{
    if(this->depth==depth)
        return;

    std::vector<Move> possible_moves = generateMoves(board,whiteToPlay,wLCastle,wRCastle,bLCastle, bRCastle);

    if(prevMove != NULL)
    {
        if(prevMove->pieceMoved=='P')
        {
            if(abs(prevMove->endRow-prevMove->startRow)==2)
            {
                char side = board[prevMove->endRow][prevMove->endCol][0];
                std::string opp;
                int dir;
                if(side=='w')
                {
                    opp = "bP";
                    dir = 1;
                }
                else
                {
                    opp = "wP";
                    dir = -1;
                }
                if(inBoard(prevMove->endRow,prevMove->endCol+1) and board[prevMove->endRow][prevMove->endCol+1]==opp)
                {
                    possible_moves.push_back(Move(std::make_pair(prevMove->endRow,prevMove->endCol+1),std::make_pair(prevMove->endRow+dir,prevMove->endCol),board));
                }
                if(inBoard(prevMove->endRow,prevMove->endCol-1) and board[prevMove->endRow][prevMove->endCol-1]==opp)
                {
                    possible_moves.push_back(Move(std::make_pair(prevMove->endRow,prevMove->endCol-1),std::make_pair(prevMove->endRow+dir,prevMove->endCol),board));
                }
            }
        }
    }
    for(Move move:possible_moves)
    {
        if(move.pieceMoved == 'K')
        {
            if(whiteToPlay)
            {
                wRCastle = false;
                wLCastle = false;
            }
            else
            {
                bRCastle = false;
                bLCastle = false;
            }
        }
        if(move.pieceMoved == 'R')
        {
            if(whiteToPlay)
            {
                if(move.startCol==0)
                    wLCastle = false;
                else
                    wRCastle = false;
            }
            else
            {
                if(move.startCol==0)
                    bLCastle = false;
                else
                    bRCastle = false;
            }
        }
        Board b = executeMove(board,move);
        TreeNode* child = new TreeNode(b.board,!whiteToPlay,wRCastle,wLCastle,bRCastle,bLCastle);
        tree->AddChild(child);
        createGameTree(child,child->board,!whiteToPlay,wRCastle,wLCastle,bRCastle,bLCastle,depth+1,&move);
    }
}

void Engine::evaluate(std::string board[8][8],bool whiteToPlay, bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle)
{
    this->wLCastle = wLCastle;
    this->wRCastle = wRCastle;
    this->bLCastle = bLCastle;
    this->bRCastle = bRCastle;
    TreeNode* tree = new TreeNode(board,whiteToPlay,wRCastle,wLCastle,bRCastle,bLCastle);
    int count = 0;
    createGameTree(tree,board,whiteToPlay,wRCastle,wLCastle,bRCastle,bLCastle);
    // TreeNode::pruneTree(tree,whiteToPlay);
    TreeNode::Print(tree,count);
    std::cout<<"Calculated "<<count<<" positions";
}

std::vector<Move> Engine::generateMoves(std::string board[8][8],bool whiteToPlay,bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle)
{
    char team;
    if(whiteToPlay)
        team = 'w';
    else
        team = 'b';

    std::vector<Move> possible_moves;
    std::vector<Move> valid_moves;

    for(int i=0;i<8;i++)
    {
        for(int j = 0;j<8;j++)
        {
            if(board[i][j][0] == team)
            {
                function_lookup[board[i][j][1]](board,std::make_pair(i,j),whiteToPlay,possible_moves,wLCastle,wRCastle,bLCastle,bRCastle);
            }
        }
    }

    for(Move move:possible_moves)
    {
        struct Board b = executeMove(board,move);
        if(!isCheck(b.board,whiteToPlay))
            valid_moves.push_back(move);
    }
    return valid_moves;
}

struct Board Engine::executeMove(std::string board[8][8],Move move)
{
    struct Board b;
    // std::cout<<"here";
    for(int i=0;i<8;i++)
    {
        for(int j=0;j<8;j++)
        {
            b.board[i][j] = board[i][j];
        }
    }
    std::string toMove = b.board[move.startRow][move.startCol];

    // Handling en passant
    if(move.pieceMoved == 'P')
    {
        int dir;
        if(toMove[0]=='w')
        {
            dir = 1;
        }
        else
        {
            dir = -1;
        }
        if(b.board[move.endRow][move.endCol] == "--" and move.startCol != move.endCol)
        {
            b.board[move.endRow+dir][move.endCol] = "--";
        }
    }

    // std::cout<<std::endl<<toMove<<std::endl;
    if(move.special == 0 or move.special>=5)
    {
        b.board[move.endRow][move.endCol] = toMove;
        if(move.special>=5)
        {
            if(move.special == 5)
            {
                // std::cout<<"here";
                b.board[move.startRow][move.startCol+1] =  std::string(1,toMove[0])+'R';
                b.board[move.startRow][7] = "--";
            }
            else
            {
                b.board[move.startRow][move.startCol-1] = std::string(1,toMove[0])+'R';
                b.board[move.startRow][0] = "--";
            }
        }
    }
    else
        b.board[move.endRow][move.endCol] = std::string(1,toMove[0])+move.key_to_piece[move.special];
    b.board[move.startRow][move.startCol] = "--";
    return b;
}

void Engine::PawnMoves(std::string board[8][8],std::pair<int,int> start,bool whiteToPlay,std::vector<Move>& moves,bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle)
{
    // Figure out how to en passant
    int promote[] = {1,2,3,4};
    int req_start,req_end,dir;
    char team,opp;
    if(whiteToPlay)
    {
        req_start = 6;
        req_end = 0;
        dir = -1;
        team = 'w';
        opp = 'b';
    }
    else
    {
        req_start = 1;
        req_end = 7;
        dir = 1;
        team = 'b';
        opp = 'w';
    }

    if(inBoard(start.first+dir,start.second) and  board[start.first+dir][start.second] == "--" )
    {
        if(start.first+dir == req_end)
        {
            for(int i:promote)
            {
                moves.push_back(Move(start,std::make_pair(start.first+dir,start.second),board,i));
            }
        }
        else
        {
            moves.push_back(Move(start,std::make_pair(start.first+dir,start.second),board));
        }
        
        if(start.first == req_start and board[start.first+2*dir][start.second] == "--" )
        {
            moves.push_back(Move(start,std::make_pair(start.first+2*dir,start.second),board));
        }
    }
    if(inBoard(start.first+dir,start.second+1) and board[start.first+dir][start.second+1][0] == opp )
    {
        if(start.first+dir == req_end)
        {
            for(int i:promote)
            {
                moves.push_back(Move(start,std::make_pair(start.first+dir,start.second+1),board,i));
            }
        }
        else
        {
            moves.push_back(Move(start,std::make_pair(start.first+dir,start.second+1),board));
        }
    }
    if(inBoard(start.first+dir,start.second-1) and board[start.first+dir][start.second-1][0] == opp )
    {
        if(start.first+dir == req_end)
        {
            for(int i:promote)
            {
                moves.push_back(Move(start,std::make_pair(start.first+dir,start.second-1),board,i));
            }
        }
        else
        {
            moves.push_back(Move(start,std::make_pair(start.first+dir,start.second-1),board));
        }
    }
}

void Engine::KnightMoves(std::string board[8][8],std::pair<int,int> start,bool whiteToPlay,std::vector<Move>& moves,bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle)
{
    std::pair<int,int> possibilities[] = {std::make_pair(start.first+1,start.second+2),std::make_pair(start.first+2,start.second+1),std::make_pair(start.first-2,start.second+1),std::make_pair(start.first+1,start.second-2),std::make_pair(start.first+2,start.second-1),std::make_pair(start.first-1,start.second+2),std::make_pair(start.first-2,start.second-1),std::make_pair(start.first-1,start.second-2)};
    char team;
    if(whiteToPlay)
        team = 'w';
    else
        team = 'b';
    
    for(std::pair<int,int> a: possibilities)
    {
        if(inBoard(a.first,a.second) and board[a.first][a.second][0] != team)
        {
            moves.push_back(Move(start,a,board));
        }
    }
}

void Engine::BishopMoves(std::string board[8][8],std::pair<int,int> start,bool whiteToPlay,std::vector<Move>& moves,bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle)
{
    std::pair<int,int> directions[] = {std::make_pair(1,1),std::make_pair(1,-1),std::make_pair(-1,1),std::make_pair(-1,-1)};

    char team,opp;
    if(whiteToPlay)
    {
        team = 'w';
        opp = 'b';
    }
    else
    {
        team = 'b';
        opp = 'w';
    }


    for(std::pair<int,int> dir: directions)
    {
        int temp_row = start.first;
        int temp_col = start.second;

        while(inBoard(temp_row+dir.first,temp_col+dir.second))
        {
            temp_row += dir.first;
            temp_col += dir.second;

            if(board[temp_row][temp_col][0] == team)
                break;
            else if(board[temp_row][temp_col][0] == opp)
            {
                moves.push_back(Move(start,std::make_pair(temp_row,temp_col),board));
                break;
            }
            else
            {
                moves.push_back(Move(start,std::make_pair(temp_row,temp_col),board));
            }
        }
    }
}

void Engine::RookMoves(std::string board[8][8],std::pair<int,int> start,bool whiteToPlay,std::vector<Move>& moves,bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle)
{
    std::pair<int,int> directions[] = {std::make_pair(1,0),std::make_pair(0,-1),std::make_pair(-1,0),std::make_pair(0,1)};

    char team,opp;
    if(whiteToPlay)
    {
        team = 'w';
        opp = 'b';
    }
    else
    {
        team = 'b';
        opp = 'w';
    }


    for(std::pair<int,int> dir: directions)
    {
        int temp_row = start.first;
        int temp_col = start.second;

        while(inBoard(temp_row+dir.first,temp_col+dir.second))
        {
            temp_row += dir.first;
            temp_col += dir.second;

            if(board[temp_row][temp_col][0] == team)
                break;
            else if(board[temp_row][temp_col][0] == opp)
            {
                moves.push_back(Move(start,std::make_pair(temp_row,temp_col),board));
                break;
            }
            else
            {
                moves.push_back(Move(start,std::make_pair(temp_row,temp_col),board));
            }
        }
    }
}

void Engine::QueenMoves(std::string board[8][8],std::pair<int,int> start,bool whiteToPlay,std::vector<Move>& moves,bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle)
{
    std::pair<int,int> directions[] = {std::make_pair(1,0),std::make_pair(0,-1),std::make_pair(-1,0),std::make_pair(0,1),std::make_pair(1,1),std::make_pair(1,-1),std::make_pair(-1,1),std::make_pair(-1,-1)};

    char team,opp;
    if(whiteToPlay)
    {
        team = 'w';
        opp = 'b';
    }
    else
    {
        team = 'b';
        opp = 'w';
    }


    for(std::pair<int,int> dir: directions)
    {
        int temp_row = start.first;
        int temp_col = start.second;

        while(inBoard(temp_row+dir.first,temp_col+dir.second))
        {
            temp_row += dir.first;
            temp_col += dir.second;

            if(board[temp_row][temp_col][0] == team)
                break;
            else if(board[temp_row][temp_col][0] == opp)
            {
                moves.push_back(Move(start,std::make_pair(temp_row,temp_col),board));
                break;
            }
            else
            {
                moves.push_back(Move(start,std::make_pair(temp_row,temp_col),board));
            }
        }
    }
}

void Engine::KingMoves(std::string board[8][8],std::pair<int,int> start,bool whiteToPlay,std::vector<Move>& moves,bool wLCastle,bool wRCastle,bool bLCastle, bool bRCastle)
{
    std::pair<int,int> directions[] = {std::make_pair(1,0),std::make_pair(0,-1),std::make_pair(-1,0),std::make_pair(0,1),std::make_pair(1,1),std::make_pair(1,-1),std::make_pair(-1,1),std::make_pair(-1,-1)};
    char team;
    int startRow,startCol = 4;
    if(whiteToPlay)
    {
        team = 'w';
        startRow = 7;
    }
    else
    {
        team = 'b';
        startRow = 0;
    }


    for(std::pair<int,int> dir: directions)
    {
        if(inBoard(start.first+dir.first,start.second+dir.second) and board[start.first+dir.first][start.second+dir.second][0] != team)
        {
            moves.push_back(Move(start,std::make_pair(start.first+dir.first,start.second+dir.second),board));
        }
    }

    if(whiteToPlay)
    {
        if(!isCheck(board,whiteToPlay))
        {
            if(wRCastle)
            {
                if(board[startRow][startCol+1]=="--" and board[startRow][startCol+2]=="--")
                {
                    board[startRow][startCol] = "--";
                    board[startRow][startCol+1] = "wK";
                    if(!isCheck(board,whiteToPlay))
                    {
                        board[startRow][startCol] = "wK";
                        board[startRow][startCol+1] = "--";
                        moves.push_back(Move(start,std::make_pair(start.first,start.second+2),board,5));
                    }
                }
            }
            if(wLCastle)
            {
                if(board[startRow][startCol-1]=="--" and board[startRow][startCol-2]=="--" and board[startRow][startCol-3]=="--")
                {
                    board[startRow][startCol] = "--";
                    board[startRow][startCol-1] = "wK";
                    if(!isCheck(board,whiteToPlay))
                    {
                        board[startRow][startCol-1] = "--";
                        board[startRow][startCol-2] = "wK";
                        if(!isCheck(board,whiteToPlay))
                        {
                            board[startRow][startCol] = "wK";
                            board[startRow][startCol-1] = "--";
                            board[startRow][startCol-2] = "--";
                            moves.push_back(Move(start,std::make_pair(start.first,start.second-2),board,6));
                        }
                    }                    
                }
            }
        }
    }
    else
    {
        if(!isCheck(board,whiteToPlay))
        {
            if(bRCastle)
            {
                if(board[startRow][startCol+1]=="--" and board[startRow][startCol+2]=="--")
                {
                    board[startRow][startCol] = "--";
                    board[startRow][startCol+1] = "bK";
                    if(!isCheck(board,whiteToPlay))
                    {
                        board[startRow][startCol] = "bK";
                        board[startRow][startCol+1] = "--";
                        moves.push_back(Move(start,std::make_pair(start.first,start.second+2),board,5));
                    }                    
                }
            }
            if(bLCastle)
            {
                if(board[startRow][startCol-1]=="--" and board[startRow][startCol-2]=="--" and board[startRow][startCol-3]=="--")
                {
                    board[startRow][startCol] = "--";
                    board[startRow][startCol-1] = "bK";
                    if(!isCheck(board,whiteToPlay))
                    {
                        board[startRow][startCol-1] = "--";
                        board[startRow][startCol-2] = "bK";
                        if(!isCheck(board,whiteToPlay))
                        {
                            board[startRow][startCol] = "bK";
                            board[startRow][startCol-1] = "--";
                            board[startRow][startCol-2] = "--";
                            moves.push_back(Move(start,std::make_pair(start.first,start.second-2),board,6));
                        }
                    }                    
                }
            }
        }
    }
}

bool Engine::isCheck(std::string board[8][8],bool whiteToPlay)
{
    std::pair<int,int> king_pos = findKing(board,whiteToPlay);
    std::pair<int,int> directions[] = {std::make_pair(1,0),std::make_pair(0,-1),std::make_pair(-1,0),std::make_pair(0,1),std::make_pair(1,1),std::make_pair(1,-1),std::make_pair(-1,1),std::make_pair(-1,-1)};

    char team,opp;
    if(whiteToPlay)
    {
        team = 'w';
        opp = 'b';
    }
    else
    {
        team = 'b';
        opp = 'w';
    }

    for(std::pair<int,int> dir: directions)
    {
        int temp_row = king_pos.first;
        int temp_col = king_pos.second;
        int count = 0;

        while(inBoard(temp_row+dir.first,temp_col+dir.second))
        {
            if(board[temp_row+dir.first][temp_col+dir.second][0] == team)
                break;
            if((dir.first+dir.second)%2 == 0)
            {
                if(board[temp_row+dir.first][temp_col+dir.second] == std::string(1,opp)+'B' or board[temp_row+dir.first][temp_col+dir.second] == std::string(1,opp)+'Q')
                    return true;
            }
            else
            {
                if(board[temp_row+dir.first][temp_col+dir.second] == std::string(1,opp)+'R' or board[temp_row+dir.first][temp_col+dir.second] == std::string(1,opp)+'Q')
                    return true;
            }
            count++;
            if(count == 1)
            {
                if(board[temp_row+dir.first][temp_col+dir.second] == std::string(1,opp)+'K')
                    return true;
            }
            temp_row += dir.first;
            temp_col += dir.second;
        }
    }

    std::pair<int,int> knightMoves[] = {std::make_pair(king_pos.first+1,king_pos.second+2),std::make_pair(king_pos.first+2,king_pos.second+1),std::make_pair(king_pos.first-2,king_pos.second+1),std::make_pair(king_pos.first+1,king_pos.second-2),std::make_pair(king_pos.first+2,king_pos.second-1),std::make_pair(king_pos.first-1,king_pos.second+2),std::make_pair(king_pos.first-2,king_pos.second-1),std::make_pair(king_pos.first-1,king_pos.second-2)};
    
    for(std::pair<int,int> dir: knightMoves)
    {
        int temp_row = king_pos.first;
        int temp_col = king_pos.second;
        if(inBoard(temp_row+dir.first,temp_col+dir.second) and board[temp_row+dir.first][temp_col+dir.second] == std::string(1,opp)+'N')
            return true;
    }
    return false;
}

std::pair<int,int> Engine::findKing(std::string board[8][8],bool whiteToPlay)
{
    std::string king;
    if(whiteToPlay)
        king = "wK";
    else
        king = "bK";

    for(int i=0;i<8;i++)
    {
        for(int j=0;j<8;j++)
        {
            if(board[i][j] == king)
                return std::make_pair(i,j);
        }
    }
}


bool Engine::inBoard(int row,int col)
{
    if(row<0 or row>7)
        return false;
    if(col<0 or col>7)
        return false;
    return true;
}


int main()
{
    std::string check[8][8] = {
        {"bR","bN","bB","bQ","bK","bB","bN","bR"},
        {"bP","bP","bP","bP","bP","bP","bP","bP"},
        {"--","--","--","--","--","--","--","--"},
        {"--","--","--","--","--","--","--","--"},
        {"--","--","--","--","--","--","--","--"},
        {"--","--","--","--","--","--","--","--"},
        {"wP","wP","wP","wP","wP","wP","wP","wP"},
        {"wR","wN","wB","wQ","wK","wB","wN","wR"}
    };

    Engine myEngine = Engine(2,2);
    myEngine.evaluate(check,true,true,true,true,true);
    // TreeNode* tree = new TreeNode(check,true,true,true,true,true,0,NULL);
    // TreeNode* tree2 = new TreeNode(check,true,true,true,true,true,0,NULL);
    // TreeNode* tree3 = new TreeNode(check,true,true,true,true,true,0,NULL);
    // TreeNode* tree4 = new TreeNode(check,true,true,true,true,true,0,NULL);
    // TreeNode* tree5 = new TreeNode(check,true,true,true,true,true,0,NULL);
    // tree->AddChild(tree2);
    
    // tree2->AddChild(tree4);
    // tree4->evaluation = 2;
    // tree5->evaluation = 4;
    // tree3->evaluation = 1;
    // int count = 0;
    // // TreeNode::Print(tree,count);
    // // std::cout<<std::endl;
    // TreeNode::pruneTree(tree,true);
    // // TreeNode::Print(tree,count);
    // tree->AddChild(tree3);
    // TreeNode::pruneTree(tree,true);
    // // TreeNode::Print(tree,count);
    // tree2->AddChild(tree5);
    // TreeNode::pruneTree(tree,true);
    // TreeNode::discard(tree,max_value);
    // TreeNode::Print(tree,count);
}