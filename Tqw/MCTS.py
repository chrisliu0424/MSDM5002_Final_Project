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
            self._unvisited_pos = self.cur_state.candidate_moves()
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
        
    def select_best_child(self, c_param=2.):
        ucb_lst = [node.UCB_weight(c_param) for node in self.children]
        #print('weights:',ucb_lst)
        #print(np.argmax(ucb_lst))
        #print([node.cur_state.cur_pos for node in self.children])
        return self.children[np.argmax(ucb_lst)]

class GameState:
    
    def __init__(self, mat, cur_pos=None, cur_player=1):
        
        self.board = mat
        self.board_size = mat.shape[0]
        self.cur_player = cur_player
        self.next_player = -1 * cur_player
        self.cur_pos = cur_pos
    
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
        if np.all(self.board != 0):
                return 0.
        size = self.board.shape[0]
        for i in range(size-5+1):
            for j in range(size-5+1):
                #print(self.board[i:i+5,j:j+5])
                res = self._five_mat_res(self.board[i:i+5,j:j+5])
                if res == None:
                    continue
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
        return [(x, y) for (x, y) in list(zip(indices[0], indices[1]))]

    
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
        return self.root.select_best_child(c_param=2.)
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
            can_pos = tmp_state.candidate_moves()
            if len(tmp_state.cur_pos)!=2:
                print(tmp_state.cur_pos)
            pos = self.rollout_policy(can_pos)
            ## state.next_state
            tmp_state = tmp_state.get_next_state(pos)
        #print('winner:',tmp_state.game_result())
        return tmp_state.game_result()
    
    def backpropagate(self,node, res):
        if node.cur_state.next_player == res:
            node._win_nums += 1.
        else:
            node._lose_nums += 1.
        node._sim_nums += 1.
        
        if node.parent:
            #print('wins:',self._win_nums)
            #print('N:',self.N())
            self.backpropagate(node.parent,res)




