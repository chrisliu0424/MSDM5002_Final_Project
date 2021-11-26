# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 11:04:42 2021

@author: TQW

MCTS:
    1. Traverse, choose the best child of each layer until reach an non-fully-expanded
    node.
    2. Expand the non-fully-expanded node by an unvisited child node (0/0)
    3. Start to rollout, get the rollout result.
    4. Backpropagate the rollout result.
"""

import numpy as np
import random
import time
from Helpers import draw_board, render, check_for_done



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
    
    def get_unvisited_pos(self):
        '''
        when unvisited pos is None,
        return the list of candidate moves
        '''
        if self._unvisited_pos is None:
            ## state.candidate_moves()
            #print('generating candidate moves...')
            #print('cur board:',self.cur_state.board)
            #self._unvisited_pos = self.cur_state.candidate_moves()
            self._unvisited_pos = self.cur_state.select_can_moves()
        return self._unvisited_pos
    
    def is_terminal(self):
        #print(self.cur_state.is_gameover())
        return self.cur_state.is_gameover()
    
    def is_fully_expanded(self):
        '''
        check has the node fully expanded
        '''
        return len(self.get_unvisited_pos()) == 0
    
    def UCB_weight(self,c_param=2):
        self._ucb = (self.Q() / self.N()) + c_param * np.sqrt((2 * np.log(self.parent.N()) / self.N()))
        return self._ucb
        
    def select_best_child(self, c_param=1.4):
        ucb_lst = [node.UCB_weight(c_param) for node in self.children]
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
    def select_can_moves(self, num = 20):
        
        can_moves = self.candidate_moves()
        if len(can_moves)<=num:
            return can_moves
        scores = []
        for move in can_moves:
            t, b, l, r = move[0]-2, move[0]+2, move[1]-2, move[1]+2
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
        
        
            if (diag_sum_tl == -5) or (diag_sum_tl == -5):
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

    def select_move_by_mcts(self, search_limit_num=None,search_limit_time=None):
        iterations = 0
        if search_limit_num:
            for i in range(search_limit_num):
                leaf = self.traverse()
                #print(leaf.cur_state.board)
                self.simulation(leaf)
                #print('leaf visited:',leaf.N())
                
        else:
            end_time = time.time() + search_limit_time
            while time.time() < end_time:
                leaf = self.traverse()
                self.simulation(leaf)
                iterations+=1
        if iterations != 0:
            print(f"{iterations} iterations in {search_limit_time}s")

        # to select best child go for exploitation only
        return self.root.select_best_child(c_param=2.0)
    def simulation(self, leaf):
        winner = self.rollout(leaf)
        self.backpropagate(leaf,winner)

    def traverse(self):
        '''
        Choose the best child in each layer
        until reach a non-fully-expanded node
        '''
        tmp_node = self.root
        tmp_ls = []
        while not tmp_node.is_terminal():
            if not tmp_node.is_fully_expanded():
                #print('traverse pos:',tmp_node.cur_state.cur_pos)
                return self.expand(tmp_node)
            else:
                #print('fully expanded')
                tmp_node = tmp_node.select_best_child()
                #print('best child:',tmp_node.cur_state.cur_pos)
            tmp_ls.append(tmp_node.cur_state.cur_player)
        return tmp_node
    def expand(self,node):
        '''
        expand the non-fully-expanded node
        choose an unvisited position as a child node
        '''
        pos = node.get_unvisited_pos().pop()
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
    
    def rollout(self,node):
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
            can_pos = tmp_state.select_can_moves()
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