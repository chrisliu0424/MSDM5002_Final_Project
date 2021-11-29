# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 10:56:14 2021

@author: TQW
"""

import pygame
import numpy as np
import time
from numpy.core.fromnumeric import diagonal
import pygame
import numpy as np
from collections import Counter
import random


class MCTSNode:
    def __init__(self,state,parent=None):
        self.cur_state = state
        self.parent = parent
        self.children = list()
        self._sim_nums = 0.
        self._win_nums = 0.
        self._lose_nums = 0.
        self._ucb = None
        self._unvisited_pos = None
        
    
    def Q(self):
        return self._win_nums
    
    def N(self):
        return self._sim_nums
    
    def get_unvisited_pos(self,r_param):
        '''
        when unvisited pos is None,
        return the list of candidate moves
        '''
        if self._unvisited_pos is None:
            ## state.candidate_moves()
            #print('generating candidate moves...')
            #print('cur board:',self.cur_state.board)
            #self._unvisited_pos = self.cur_state.candidate_moves()
            self._unvisited_pos = self.cur_state.select_can_moves(r_param=r_param)
        return self._unvisited_pos
    
    def is_terminal(self):
        #print(self.cur_state.is_gameover())
        return self.cur_state.is_gameover()
    
    def is_fully_expanded(self,r_param):
        '''
        check has the node fully expanded
        '''
        return len(self.get_unvisited_pos(r_param=r_param)) == 0
    
    def UCB_weight(self,c_param):
        self._ucb = (self.Q() / self.N()) + c_param * np.sqrt((2 * np.log(self.parent.N()) / self.N()))
        return self._ucb
        
    def select_best_child(self, c_param):
        ucb_lst = [node.UCB_weight(c_param) for node in self.children]
        if len(ucb_lst)==0:
            print(self.cur_state.board)
        #print('weights:',ucb_lst)
        #print(np.argmax(ucb_lst))
        #print([node.cur_state.cur_pos for node in self.children])
        return self.children[np.argmax(ucb_lst)]

class GameState:
    
    def __init__(self, mat, last_pos=None, cur_player=1):
        
        self.board = mat
        self.board_size = mat.shape[0]
        self.cur_player = cur_player
        self.next_player = -1 * cur_player
        self.last_pos = last_pos
    
    def _five_mat_res(self,mat):
        rowsum = np.sum(mat, 0)
        colsum = np.sum(mat, 1)
        diag_sum_tl = mat.trace()
        diag_sum_tr = mat[::-1].trace()

        player_one_wins = any(rowsum == 5)
        player_one_wins += any(colsum == 5)
        player_one_wins += (diag_sum_tl == 5)
        player_one_wins += (diag_sum_tr == 5)

        if player_one_wins:
            return 1

        player_two_wins = any(rowsum == -5)
        player_two_wins += any(colsum == -5)
        player_two_wins += (diag_sum_tl == -5)
        player_two_wins += (diag_sum_tr == -5)

        if player_two_wins:
            return -1
        # if not over - no result
        return None
    def game_result(self):
        # size = self.board.shape[0]
        # for i in range(size-5+1):
        #     for j in range(size-5+1):
        #         #print(self.board[i:i+5,j:j+5])
        #         res = self._five_mat_res(self.board[i:i+5,j:j+5])
        #         if res == None:
        #             continue
        #         else:
        #             return res
        # if np.all(self.board != 0):
        #         return 0.
        flag, res = self.check_for_done_roll()
        if flag == False:
            return None
        else:
            return res

    def is_gameover(self):
        
        return self.game_result() is not None
    
    def get_next_state(self, pos):
        #print(self.board)
        new_board = np.copy(self.board)
        new_board[pos[0], pos[1]] = self.cur_player
        return GameState(new_board, pos, self.next_player)
    
    def candidate_moves(self):
        #print(self.board)
        indices = np.where(self.board == 0)
        can_pos = [(x, y) for (x, y) in list(zip(indices[0], indices[1]))]
        #random.shuffle(can_pos)
        return can_pos
    def select_can_moves(self,r_param,num = 20):
        # r is a tuning parameter related to the range of positions to calculate weights,
        can_moves = self.candidate_moves()
        if len(can_moves)<=num:
            return can_moves
        scores = []
        for move in can_moves:
            t, b, l, r = move[0]-r_param, move[0]+r_param, move[1]-r_param, move[1]+r_param
            if t < 0:
                t = 0
            elif b > len(self.board)-1:
                b = len(self.board)-1
            if l < 0:
                l = 0
            elif r > len(self.board)-1:
                r = len(self.board)-1
            sur = self.board[t:b+1,l:r+1]
            score = len(np.where(sur!=0)[0])
            scores.append(score)
        indices_scores = [(t,s) for (t,s) in list(zip(can_moves,scores)) if s!=0]
        indices_scores = sorted(indices_scores,key = lambda x:x[1])
        can_moves = [t[0] for t in indices_scores[-num:]]
        
        return can_moves
    def check_for_done_roll(self):
        def _five_mat_res_new(mat):
            """"
            Only check for diagonal entry
            """
            diag_sum_tl = mat.trace()
            diag_sum_tr = mat[::-1].trace()
        
            if (diag_sum_tl == 5) or (diag_sum_tr == 5):
                return 1
        
        
            if (diag_sum_tl == -5) or (diag_sum_tr == -5):
                return -1
        
            # if not over - no result
            return None
        mat = self.board
        if self.last_pos:
            # manually get into the exception clause
            pos=self.last_pos
            row,col = pos[0],pos[1]         
            player = mat[row,col]
            top = 0 if row-4<0 else row-4               # define the upper bound, lower bound, left bound and right bound for the check condition
            bottom = 7 if row+4>7 else row+4
            left = 0 if col-4<0 else col-4
            right = 7 if col+4>7 else col+4
            ones5 = np.ones(5)
            # print("into try")              # debug message to check if the mat is into try or exception
            
            # Check if horizontal made 5 connects
            temp_left = left
            while temp_left+4<=right:
                if np.matmul(mat[row,temp_left:temp_left+5],ones5) == 5*player:
                    return True,player
                temp_left+=1
            # print("position1")
            # Check for the vertical
            temp_top = top
            while temp_top+4<=bottom:
                if np.matmul(mat[temp_top:temp_top+5,col],ones5) == 5*player:
                    return True,player
                temp_top+=1
            # print("position2")
            # # Check for the diagonal
            temp_col = col-5
            temp_row = row-5
            while temp_col<=7 and temp_row<=7:
                if temp_col<0 or temp_row<0:
                    pass
                else:
                    if(np.sum(mat[temp_row:temp_row+5,temp_col:temp_col+5].diagonal())==5*player):
                        return True,player
                temp_col+=1
                temp_row+=1
            # print("position3")
            # Check for the off-diagonal
            temp_col = col
            temp_row = row
            while temp_col<=7 and temp_row<=7:
                if(np.sum(np.fliplr(mat[temp_row:temp_row+5,temp_col-4:temp_col+1]).diagonal())==5*player):
                    return True,player
                temp_col+=1
                temp_row-=1
            if np.sum(mat==0)==0:
                return True,0
            else:
                return False,0
    
        else:                             # if last_map not even exist, this is the first step
        
            # print("get into the exception")              # debug message
            # if last_mat does not exist or does not match condition, we perpare this mat to be last_mat as we call next time
            size = mat.shape[0]
            if np.sum([mat==0]) > (size*size-9):     # if less than 9 moves, no winner
                return False,0
            ones8 = np.ones(8)
            mat1 = mat.copy()
            mat1[mat1==-1] = 0                 # mat1 only keeps 1 in the mat
            mat2 = mat.copy()
            mat2[mat1==1] = 0
            mat2 = mat2*(-1)                   # mat2 only keeps -1 in the mat, but convert all -1 to 1 for future calculation
            
            rowsum = np.matmul(mat1,ones8)
            colsum = np.matmul(ones8, mat1)
            row_to_check=[index for index,value in enumerate(rowsum) if value>4]
            col_to_check=[index for index,value in enumerate(colsum) if value>4]
    
            rowsum2 = np.matmul(mat2,ones8)
            colsum2 = np.matmul(ones8, mat2)
            row_to_check2 = [index for index,value in enumerate(rowsum2) if value>4]
            col_to_check2 = [index for index,value in enumerate(colsum2) if value>4]
    
            for row in row_to_check:
                for col_index in range(0,size-4):
                    if np.matmul(mat1[row,col_index:col_index+5],ones8[:5]) == 5:
                        return True,1
            for col in col_to_check:
                for row_index in range(0,size-4):
                    if np.matmul(mat1[row_index:row_index+5,col],ones8[:5]) == 5:
                        return True,1 
            
            for row in row_to_check2:
                for col_index in range(0,size-4):
                    if np.matmul(mat2[row,col_index:col_index+5],ones8[:5]) == 5:
                        return True,-1
            for col in col_to_check2:
                for row_index in range(0,size-4):
                    if np.matmul(mat2[row_index:row_index+5,col],ones8[:5]) == 5:
                        return True,-1 
    
            for i in range(size-5+1):
                for j in range(size-5+1):
                    res = _five_mat_res_new(mat[i:i+5,j:j+5])
                    if res == None:
                        continue
                    else:
                        return True, res
            if np.all(mat != 0):
                return True, 0
            return False,0
                  
class MCTS:
    def __init__(self, node):
        self.root = node

    def select_move_by_mcts(self,r_param,c_param, search_limit_num=None,search_limit_time=None):
        iterations = 0
        if search_limit_num:
            for i in range(search_limit_num):
                leaf = self.traverse(r_param=r_param,c_param=c_param)
                #print(leaf.cur_state.board)
                self.simulation(leaf,r_param=r_param)
                #print('leaf visited:',leaf.N())
                
        else:
            end_time = time.time() + search_limit_time
            while time.time() < end_time:
                leaf = self.traverse(r_param=r_param,c_param=c_param)
                self.simulation(leaf,r_param=r_param)
                iterations+=1
        # if iterations != 0:
            # print(f"{iterations} iterations in {search_limit_time}s")

        # to select best child go for exploitation only
        return self.root.select_best_child(c_param=c_param)
    def simulation(self, leaf,r_param):
        winner = self.rollout(leaf,r_param=r_param)
        self.backpropagate(leaf,winner)

    def traverse(self,r_param,c_param):
        '''
        Choose the best child in each layer
        until reach a non-fully-expanded node
        '''
        tmp_node = self.root
        tmp_ls = []
        while not tmp_node.is_terminal():
            if not tmp_node.is_fully_expanded(r_param=r_param):
                #print('traverse pos:',tmp_node.cur_state.cur_pos)
                return self.expand(tmp_node,r_param=r_param)
            else:
                #print('fully expanded')
                tmp_node = tmp_node.select_best_child(c_param=c_param)
                #print('best child:',tmp_node.cur_state.cur_pos)
            tmp_ls.append(tmp_node.cur_state.cur_player)
        return tmp_node
    def expand(self,node,r_param):
        '''
        expand the non-fully-expanded node
        choose an unvisited position as a child node
        '''
        pos = node.get_unvisited_pos(r_param=r_param).pop()
        #print(self.get_unvisited_pos())
        next_state = node.cur_state.get_next_state(pos)
        child = MCTSNode(next_state,node)
        node.children.append(child)
        return child
    

    
    def rollout_policy(self,can_pos):
        '''
        Rewrite by more intellegent strategy
        '''
        return random.sample(can_pos,1)[0]
    
    def rollout(self,node,r_param):
        '''
        Return -1 1 or 0
        -------
        from the leaf node, start to rollout
        until reach the terminal node

        '''
        tmp_state = node.cur_state
        while not tmp_state.is_gameover():
            #print(tmp_state.board)
            #can_pos = tmp_state.candidate_moves()
            can_pos = tmp_state.select_can_moves(r_param=r_param)
            #if len(tmp_state.cur_pos)!=2:
                #print(tmp_state.cur_pos)
            pos = self.rollout_policy(can_pos)
            ## state.next_state
            tmp_state = tmp_state.get_next_state(pos)
        #print('winner:',tmp_state.game_result())
        return tmp_state.game_result()
    
    def backpropagate(self,node, res):
        if node.cur_state.next_player == res:
            node._lose_nums += 1.
        else:
            node._win_nums += 1.
        node._sim_nums += 1.
        
        if node.parent:
            #print('wins:',self._win_nums)
            #print('N:',self.N())
            self.backpropagate(node.parent,res)
def update_by_man(event,mat):
    """
    This function detects the mouse click on the game window. Update the state matrix of the game. 
    input: 
        event:pygame event, which are either quit or mouse click)
        mat: 2D matrix represents the state of the game
    output:
        mat: updated matrix
    """
    global M
    done=False
    if event.type==pygame.QUIT:
        done=True
    if event.type==pygame.MOUSEBUTTONDOWN:
        (x,y)=event.pos
        row = round((y - 40) / 40)     
        col = round((x - 40) / 40)
        mat[row][col]=1
    return mat, done
def draw_board(screen):    
    """
    This function draws the board with lines
    input: game windows
    output: none
    """
    global M
    M=8
    d=int(560/(M-1))
    black_color = [0, 0, 0]
    board_color = [ 241, 196, 15 ]
    screen.fill(board_color)
    for h in range(0, M):
        pygame.draw.line(screen, black_color,[40, h * d+40], [600, 40+h * d], 1)
        pygame.draw.line(screen, black_color, [40+d*h, 40], [40+d*h, 600], 1)
def draw_stone(screen, mat):
    """
    This functions draws the stones according to the mat. It draws a black circle for matrix element 1(human),
    it draws a white circle for matrix element -1 (computer)
    input:
        screen: game window, onto which the stones are drawn
        mat: 2D matrix representing the game state
    output:
        none
    """
    black_color = [0, 0, 0]
    white_color = [255, 255, 255]
    M=len(mat)
    d=int(560/(M-1))
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if mat[i][j]==1:
                pos = [40+d * j, 40+d* i ]
                pygame.draw.circle(screen, black_color, pos, 18,0)
            elif mat[i][j]==-1:
                pos = [40+d* j , 40+d * i]
                pygame.draw.circle(screen, white_color, pos, 18,0)

def render(screen, mat):
    """
    Draw the updated game with lines and stones using function draw_board and draw_stone
    input:
        screen: game window, onto which the stones are drawn
        mat: 2D matrix representing the game state
    output:
        none        
    """
    
    draw_board(screen)
    draw_stone(screen, mat)
    pygame.display.update()

# =============================================================================
# # Check for done function by TQW
# def check_for_done(mat):
#     """
#     please write your own code testing if the game is over. Return a boolean variable done. If one of the players wins
#     or the tie happens, return True. Otherwise return False. Print a message about the result of the game.
#     input: 
#         2D matrix representing the state of the game
#     output:
#         True,1:Black win the game
#         True,0:Draw
#         True,-1:White win the game
#         False,0:Not complete
#     """
#     def _five_mat_res(mat):
#         rowsum = np.sum(mat, 0)
#         colsum = np.sum(mat, 1)
#         diag_sum_tl = mat.trace()
#         diag_sum_tr = mat[::-1].trace()
# 
#         player_one_wins = any(rowsum == 5)
#         player_one_wins += any(colsum == 5)
#         player_one_wins += (diag_sum_tl == 5)
#         player_one_wins += (diag_sum_tr == 5)
# 
#         if player_one_wins:
#             return 1
# 
#         player_two_wins = any(rowsum == -5)
#         player_two_wins += any(colsum == -5)
#         player_two_wins += (diag_sum_tl == -5)
#         player_two_wins += (diag_sum_tr == -5)
# 
#         if player_two_wins:
#             return -1
#         # if not over - no result
#         return None
# 
#     size = mat.shape[0]
#     for i in range(size-5+1):
#         for j in range(size-5+1):
#             #print(self.board[i:i+5,j:j+5])
#             res = _five_mat_res(mat[i:i+5,j:j+5])
#             if res == None:
#                 continue
#             else:
#                 return True, res
#     if np.all(mat != 0):
#         return True, 0
#     return False,0
# =============================================================================

def _five_mat_res_new(mat):
    """"
    Only check for diagonal entry
    """
    diag_sum_tl = mat.trace()
    diag_sum_tr = mat[::-1].trace()

    if (diag_sum_tl == 5) or (diag_sum_tr == 5):
        return 1


    if (diag_sum_tl == -5) or (diag_sum_tr == -5):
        return -1

    # if not over - no result
    return None


# Check for done function written by Chris on Nov.11
# Using the difference of last_mat and mat to find the last position, and determine only by the relative 
#### This check_for_done is 4 times faster than the standard one ######################
# def check_for_done(mat):
#     global last_mat
#     try:
#         if len((np.where(abs(mat-last_mat)==1))[0])!=1:
#             last_mat = mat.copy()
#             print(tt)                   # manually get into the exception clause
#         pos=[int(x) for x in np.where(abs(mat-last_mat)==1)]
#         last_mat = mat.copy()
#         row,col = pos[0],pos[1]         
#         player = mat[row,col]
#         top = 0 if row-4<0 else row-4               # define the upper bound, lower bound, left bound and right bound for the check condition
#         bottom = 7 if row+4>7 else row+4
#         left = 0 if col-4<0 else col-4
#         right = 7 if col+4>7 else col+4
#         ones5 = np.ones(5)
#         # print("into try")              # debug message to check if the mat is into try or exception
        
#         # Check if horizontal made 5 connects
#         temp_left = left
#         while temp_left+4<=right:
#             if np.matmul(mat[row,temp_left:temp_left+5],ones5) == 5*player:
#                 return True,player
#             temp_left+=1
#         # print("position1")
#         # Check for the vertical
#         temp_top = top
#         while temp_top+4<=bottom:
#             if np.matmul(mat[temp_top:temp_top+5,col],ones5) == 5*player:
#                 return True,player
#             temp_top+=1
#         # print("position2")
#         # # Check for the diagonal
#         temp_col = col-5
#         temp_row = row-5
#         while temp_col<=7 and temp_row<=7:
#             if temp_col<0 or temp_row<0:
#                 pass
#             else:
#                 if(np.sum(mat[temp_row:temp_row+5,temp_col:temp_col+5].diagonal())==5*player):
#                     return True,player
#             temp_col+=1
#             temp_row+=1
#         # print("position3")
#         # Check for the off-diagonal
#         temp_col = col
#         temp_row = row
#         while temp_col<=7 and temp_row<=7:
#             if(np.sum(np.fliplr(mat[temp_row:temp_row+5,temp_col-4:temp_col+1]).diagonal())==5*player):
#                 return True,player
#             temp_col+=1
#             temp_row-=1
#         if np.sum(mat==0)==0:
#             return True,0
#         else:
#             return False,0

#     except:                             # if last_map not even exist, this is the first step
    
#         # print("get into the exception")              # debug message
#         # if last_mat does not exist or does not match condition, we perpare this mat to be last_mat as we call next time
#         last_mat = mat.copy()           
#         size = mat.shape[0]
#         if np.sum([mat==0]) > (size*size-9):     # if less than 9 moves, no winner
#             return False,0
#         ones8 = np.ones(8)
#         mat1 = mat.copy()
#         mat1[mat1==-1] = 0                 # mat1 only keeps 1 in the mat
#         mat2 = mat.copy()
#         mat2[mat1==1] = 0
#         mat2 = mat2*(-1)                   # mat2 only keeps -1 in the mat, but convert all -1 to 1 for future calculation
        
#         rowsum = np.matmul(mat1,ones8)
#         colsum = np.matmul(ones8, mat1)
#         row_to_check=[index for index,value in enumerate(rowsum) if value>4]
#         col_to_check=[index for index,value in enumerate(colsum) if value>4]

#         rowsum2 = np.matmul(mat2,ones8)
#         colsum2 = np.matmul(ones8, mat2)
#         row_to_check2 = [index for index,value in enumerate(rowsum2) if value>4]
#         col_to_check2 = [index for index,value in enumerate(colsum2) if value>4]

#         for row in row_to_check:
#             for col_index in range(0,size-4):
#                 if np.matmul(mat1[row,col_index:col_index+5],ones8[:5]) == 5:
#                     return True,1
#         for col in col_to_check:
#             for row_index in range(0,size-4):
#                 if np.matmul(mat1[row_index:row_index+5,col],ones8[:5]) == 5:
#                     return True,1 
        
#         for row in row_to_check2:
#             for col_index in range(0,size-4):
#                 if np.matmul(mat2[row,col_index:col_index+5],ones8[:5]) == 5:
#                     return True,-1
#         for col in col_to_check2:
#             for row_index in range(0,size-4):
#                 if np.matmul(mat2[row_index:row_index+5,col],ones8[:5]) == 5:
#                     return True,-1 

#         for i in range(size-5+1):
#             for j in range(size-5+1):
#                 res = _five_mat_res_new(mat[i:i+5,j:j+5])
#                 if res == None:
#                     continue
#                 else:
#                     return True, res
#         if np.all(mat != 0):
#             return True, 0
#         return False,0

import numpy as np
from collections import Counter

def _stop_four_connect(mat):
    """"
    find potential position to stop four opponent connected chess 
    input:
        mat: 5*5 matrix
    output:
        tuple of the position to stop
    """
    # For row
    for row in range(len(mat)):
        temp_count = Counter(mat[row,:])
        if temp_count[0]==1 and temp_count[1]==4:
            return (row,np.where(mat[row,:]==0)[0][0])
    # For col
    for col in range(len(mat)):
        temp_count = Counter(mat[:,col])
        if temp_count[0]==1 and temp_count[1]==4:
            return (np.where(mat[:,col]==0)[0][0],col)
    # For diagonal
    temp_count = Counter(mat.diagonal())
    if temp_count[0]==1 and temp_count[1]==4:
        # print(np.where(mat.diagonal()==0))
        return (np.where(mat.diagonal()==0)[0][0],np.where(mat.diagonal()==0)[0][0])
    # For off diagonal
    temp_count = Counter(mat[::-1].diagonal())
    if temp_count[0]==1 and temp_count[1]==4:
        # print(mat[::-1].diagonal())
        return (np.where(mat[::-1].diagonal()[::-1]==0)[0][0],len(mat)-1-np.where(mat[::-1].diagonal()[::-1]==0)[0][0])

def _stop_three_connect(mat):
    """"
    find potential position to stop three opponent connected chess (保守版，00111和11100不拦截)
    input:
        mat: 5*5 matrix
    output:
        tuple of the position to stop
    """
    choice = np.random.choice([0,1])
    skip_array = [0,0,1,1,1]
    
    # For row
    for row in range(len(mat)):
        if np.array_equal(mat[row,:],skip_array) or np.array_equal(mat[row,:],skip_array[::-1]):
            continue
        temp_count = Counter(mat[row,:])
        if temp_count[0]==2 and temp_count[1]==3:
            return (row,np.where(mat[row,:]==0)[0][choice])
    # For col
    for col in range(len(mat)):
        if np.array_equal(mat[:,col],skip_array) or np.array_equal(mat[:,col],skip_array[::-1]):
            continue
        temp_count = Counter(mat[:,col])
        if temp_count[0]==2 and temp_count[1]==3:
            return (np.where(mat[:,col]==0)[0][choice],col)
    # For diagonal
    temp_count = Counter(mat.diagonal())
    if np.array_equal(mat.diagonal(),skip_array) or np.array_equal(mat.diagonal(),skip_array[::-1]):
            pass
    else:
        if temp_count[0]==2 and temp_count[1]==3:
            return (np.where(mat.diagonal()==0)[0][choice],np.where(mat.diagonal()==0)[0][choice])
    # For off diagonal
    temp_count = Counter(mat[::-1].diagonal())
    if np.array_equal(mat[::-1].diagonal()[::-1],skip_array) or np.array_equal(mat[::-1].diagonal()[::-1],skip_array[::-1]):
            pass
    else:
        if temp_count[0]==2 and temp_count[1]==3:
            return (np.where(mat[::-1].diagonal()[::-1]==0)[0][choice],len(mat)-1-np.where(mat[::-1].diagonal()[::-1]==0)[0][choice])
    return None



# def _stop_three_connect(mat):
#     """"
#     find potential position to stop three opponent connected chess (开放版，只拦截01110)
#     input:
#         mat: 5*5 matrix
#     output:
#         tuple of the position to stop
#     """
#     choice = np.random.choice([0,4])
#     check_arr = np.array([0,1,1,1,0])       # only cut 01110
    
#     # For row
#     for row in range(len(mat)):
#         if np.array_equal(mat[row,:],check_arr):
#             return (row,choice)
#     # For col
#     for col in range(len(mat)):
#         if np.array_equal(mat[:,col],check_arr):
#             return (choice,col)
#     # For diagonal
#     if np.array_equal(mat.diagonal(),check_arr):
#         return (choice,choice)
#     # For off diagonal
#     if np.array_equal(mat[::-1].diagonal(),check_arr):
#         return (choice,len(mat)-1-choice)
#     return None

def find_cut_position(mat):
    size = mat.shape[0]
    for i in range(size-5+1):
        for j in range(size-5+1):
            pos_for_four_self = _stop_four_connect(-mat[i:i+5,j:j+5])
            if pos_for_four_self:
                # print(f"pos_for_four_self,{[(pos_for_four_self[0]+i),pos_for_four_self[1]+j]}")
                return ((pos_for_four_self[0]+i),pos_for_four_self[1]+j)
    for i in range(size-5+1):
        for j in range(size-5+1):
            pos_for_four_oppo = _stop_four_connect(mat[i:i+5,j:j+5])
            if pos_for_four_oppo:
                # print(f"pos_for_four_oppo,{[(pos_for_four_oppo[0]+i),pos_for_four_oppo[1]+j]}")
                return ((pos_for_four_oppo[0]+i),pos_for_four_oppo[1]+j)
    for i in range(size-5+1):
        for j in range(size-5+1):
            pos_for_three_self = _stop_three_connect(-mat[i:i+5,j:j+5])
            if pos_for_three_self:
                # print(f"pos_for_three_self,{[(pos_for_three_self[0]+i),pos_for_three_self[1]+j]}")
                return ((pos_for_three_self[0]+i),pos_for_three_self[1]+j)
            
    for i in range(size-5+1):
        for j in range(size-5+1):
            pos_for_three_oppo = _stop_three_connect(mat[i:i+5,j:j+5])
            if pos_for_three_oppo:
                # print(f"cut for pos_for_three_oppo,{[pos_for_three_oppo[0]+i,pos_for_three_oppo[1]+j]}")
                return ((pos_for_three_oppo[0]+i),pos_for_three_oppo[1]+j)
def update_by_pc(mat,c_param,r_param):
    """
    This is the core of the game. Write your code to give the computer the intelligence to play a Five-in-a-Row game 
    with a human
    input:
        2D matrix representing the state of the game.
    output:
        2D matrix representing the updated state of the game.
    """
    if np.all(mat == 0):
        mat[len(mat)//2, len(mat)//2] = 1
        return mat
    # Look for cutting position first, if cut_pos==None, continue with the MCTS
    #s = time.time()
    cut_pos = find_cut_position(-mat)
    #print(time.time()-s)
    if cut_pos:
        time.sleep(1)
        mat[cut_pos]=1
        return mat
    board_state = GameState(mat = mat)
    root = MCTSNode(state = board_state)
    mcts = MCTS(root)
    # best_node = mcts.select_move_by_mcts(search_limit_num=2000)                    # Specify number of iterations in one move
    best_node = mcts.select_move_by_mcts(search_limit_time=5,r_param=2,c_param=2)                       # Specify iterations time in one move
    return best_node.cur_state.board