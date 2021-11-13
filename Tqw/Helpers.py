# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 10:55:58 2021

@author: TQW
"""
import pygame
import numpy as np

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
    This function draws the board with lines.
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
def check_for_done(mat):
    """
    please write your own code testing if the game is over. Return a boolean variable done. If one of the players wins
    or the tie happens, return True. Otherwise return False. Print a message about the result of the game.
    input: 
        2D matrix representing the state of the game
    output:
        True,1:Black win the game
        True,0:Draw
        True,-1:White win the game
        False,0:Not complete
    """
    def _five_mat_res(mat):
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
    if np.all(mat != 0):
        return True,0.
    size = mat.shape[0]
    for i in range(size-5+1):
        for j in range(size-5+1):
            #print(self.board[i:i+5,j:j+5])
            res = _five_mat_res(mat[i:i+5,j:j+5])
            if res == None:
                continue
            else:
                return True, res
    return False,0