# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 11:17:05 2021

@author: TQW
"""

import pygame
import numpy as np
from Helpers import draw_board, render, check_for_done
from MCTS import GameState, MCTSNode, MCTS
    
def main():
    # for debuging the check_for_done by Chris and rollout
    global M
    M=8
    pygame.init()
    screen=pygame.display.set_mode((640,640))
    pygame.display.set_caption('Five-in-a-Row')
    done=False
    mat=np.zeros((M,M))
    d=int(560/(M-1))
    draw_board(screen)
    pygame.display.update()

    
    while not done:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                done=True
            if event.type==pygame.MOUSEBUTTONDOWN:
                (x,y)=event.pos
                row = round((y - 40) / d)     
                col = round((x - 40) / d)
                mat[row][col]=1
                render(screen, mat)
                # check for win or tie
                # print message if game finished
                # otherwise contibue
                done, res = check_for_done(mat)
                if done:
                    print(res,'win !')
                    break
                
                # get the next move from computer/MCTS
                # check for win or tie
                # print message if game finished
                # otherwise contibue
                mat = -update_by_pc(-mat)
                done, res = check_for_done(mat)
                if done:
                    print(res,'win !')
                    break
                render(screen, mat)
                    
    
    pygame.quit()

def update_by_pc(mat):
    """
    This is the core of the game. Write your code to give the computer the intelligence to play a Five-in-a-Row game 
    with a human
    input:
        2D matrix representing the state of the game.
    output:
        2D matrix representing the updated state of the game.
    """
    board_state = GameState(mat = mat)
    root = MCTSNode(state = board_state)
    mcts = MCTS(root)
    # best_node = mcts.select_move_by_mcts(search_limit_num=2000)                    # Specify number of iterations in one move
    best_node = mcts.select_move_by_mcts(search_limit_time=5)                       # Specify iterations time in one move
    return best_node.cur_state.board

if __name__ == '__main__':
    main()