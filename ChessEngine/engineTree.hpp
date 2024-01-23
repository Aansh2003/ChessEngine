#include <string>
#include <vector>
#include <iostream>
#include "Moves.hpp"
#include <algorithm>


int DEF = 696969;
float max_value;

class TreeNode
{
    public:
        TreeNode(std::string[8][8],bool,bool,bool,bool,bool); //First tree construct
        TreeNode(std::string[8][8],bool,bool,bool,bool,bool,int,Move*,TreeNode* = NULL); //First tree construct
        void AddChild(TreeNode*); // Adds a child to tree
        bool isLeaf(); // Checks if node is a leaf
        std::vector<TreeNode*> children; // Children nodes
        std::string board[8][8]; // Currently held position
        int depth;
        float evaluation;
        static void Print(TreeNode*,int&);
        bool whiteToPlay,wRCastle,wLCastle,bRCastle,bLCastle;
        Move* prev;
        TreeNode* searchPosition(std::string[8][8],TreeNode* root);
        static void pruneTree(TreeNode* tree,bool);
        static float findEval(TreeNode*,bool);
        static float minmaxAlg(std::vector<TreeNode*>&,bool whiteToPlay);
        static void discard(TreeNode*&,float);
        static void freeNode(TreeNode*);

        TreeNode* parent;
};


TreeNode::TreeNode(std::string board[][8],bool whiteToPlay,bool wRCastle,bool wLCastle,bool bRCastle,bool bLCastle)
{
    for(int i=0;i<8;i++)
    {
        for(int j=0;j<8;j++)
        {
            this->board[i][j] = board[i][j];
        }
    }
    this->whiteToPlay = whiteToPlay;
    this->wRCastle = wRCastle;
    this->wLCastle = wLCastle;
    this->bRCastle = bRCastle;
    this->bLCastle = bLCastle;
}

TreeNode::TreeNode(std::string board[][8],bool whiteToPlay,bool wRCastle,bool wLCastle,bool bRCastle,bool bLCastle,int depth,Move* prev,TreeNode* parent)
{
    for(int i=0;i<8;i++)
    {
        for(int j=0;j<8;j++)
        {
            this->board[i][j] = board[i][j];
        }
    }
    this->whiteToPlay = whiteToPlay;
    this->wRCastle = wRCastle;
    this->wLCastle = wLCastle;
    this->bRCastle = bRCastle;
    this->bLCastle = bLCastle;
    this->depth = depth;
    this->prev = prev;
    this->evaluation = DEF;
    this->parent = parent;
}

void TreeNode::AddChild(TreeNode* tree)
{
    children.push_back(tree);
}

bool TreeNode::isLeaf()
{
    if(children.size()==0)
        return true;
    return false;
}

void TreeNode::Print(TreeNode* tree,int& count)
{
    std::cout<<tree->evaluation<<std::endl;
    if(tree->isLeaf())
    {
        count++;
        return;
    }
    for(TreeNode* children: tree->children)
    {
        Print(children,count);
    }
}

void TreeNode::pruneTree(TreeNode* root,bool whiteToPlay)
{
    root->evaluation = findEval(root,whiteToPlay);
    // int c=0;
    // Print(root,c);
    discard(root,root->evaluation);
}

float TreeNode::findEval(TreeNode* root,bool whiteToPlay)
{
    return minmaxAlg(root->children,whiteToPlay);
}

float TreeNode::minmaxAlg(std::vector<TreeNode*>& values,bool whiteToPlay)
{
    if(whiteToPlay)
    {
        float max_v = -__FLT_MAX__;
        for(TreeNode* val:values)
        {
            if(val->evaluation==DEF)
                val->evaluation = minmaxAlg(val->children,!whiteToPlay);
            if(val->evaluation!=DEF and val->evaluation>max_v)
                max_v = val->evaluation;
        }
        return (max_v==-__FLT_MAX__)?DEF:max_v;
    }
    else
    {
        float max_v = __FLT_MAX__;
        for(TreeNode* val:values)
        {
            if(val->evaluation==DEF)
                val->evaluation = minmaxAlg(val->children,!whiteToPlay);
            if(val->evaluation!=DEF and val->evaluation<max_v)
                max_v = val->evaluation;
        }
        return (max_v==__FLT_MAX__)?DEF:max_v;
    }
}

void TreeNode::discard(TreeNode*& tree,float max_value)
{
    std::vector<TreeNode*>::iterator ptr; 
    for(ptr=tree->children.begin();ptr<tree->children.end();ptr++)
    {
        TreeNode* child = *ptr;
        if(child->evaluation!=max_value)
        {
            freeNode(child);
        }
        else
        {
            discard(child,max_value);
        }
    }
}

void TreeNode::freeNode(TreeNode* tree)
{
    std::vector<TreeNode*>::iterator ptr;
    std::vector<TreeNode*> delete_vec;
    delete_vec.push_back(tree);
    for(TreeNode* element:delete_vec)
    {
        for(TreeNode* children:element->children)
        {
            delete_vec.push_back(children);
            std::cout<<children->evaluation;
        }
    }
    while(delete_vec.size()!=0)
    {
        TreeNode* toDelete = delete_vec[delete_vec.size()-1];
        delete_vec.pop_back();
        delete toDelete;
    }
}