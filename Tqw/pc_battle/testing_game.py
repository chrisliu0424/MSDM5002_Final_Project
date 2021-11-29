# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 11:03:06 2021

@author: TQW
"""
import g12### import first model,put the file under the same folder 
import g3### import second model,put the file under the same folder
import numpy as np
import pygame
import time

def update_by_man(event,mat):
    """
    This function detects the mouse click on the game window. Update the state matrix of the game. 
    input: 
        event:pygame event, which are either quit or mouse click)
        mat: 2D matrix represents the state of the game
    output:
        mat: updated matrix
    """
    done=False
    if event.type==pygame.QUIT:
        done=True
    if event.type==pygame.MOUSEBUTTONDOWN:
        (x,y)=event.pos
        row = round((y - 40) / 40)     
        col = round((x - 40) / 40)
        mat[row][col]=1
    return mat, done
def draw_board(screen, size):
    screen.fill((230, 185, 70))
    for x in range(size):
        pygame.draw.line(screen, [0, 0, 0], [25 + 50 * x, 25], [25 + 50 * x, size*50-25], 1)
        pygame.draw.line(screen, [0, 0, 0], [25, 25 + 50 * x], [size*50-25, 25 + 50 * x], 1)
    pygame.display.update()


def update_board(screen, state):
    indices = np.where(state != 0)
    for (row, col) in list(zip(indices[0], indices[1])):
        if state[row][col] == 1:
            pygame.draw.circle(screen, [0, 0, 0], [25 + 50 * col, 25 + 50 * row], 15, 15)
        elif state[row][col] == -1:
            pygame.draw.circle(screen, [255, 255, 255], [25 + 50 * col, 25 + 50 * row], 15, 15)
    pygame.display.update()
    
    
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
    #M=len(mat)
    d=int(560/(M-1))
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if mat[i][j]==1:
                pos = [40+d * j, 40+d* i ]
                pygame.draw.circle(screen, black_color, pos, 18,0)
            elif mat[i][j]==-1:
                pos = [40+d* j , 40+d * i]
                pygame.draw.circle(screen, white_color, pos, 18,0)


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
def check_for_done(mat):
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

def update_by_pc(mat):
    """
    This is the core of the game. Write your code to give the computer the intelligence to play a Five-in-a-Row game 
    with a human
    input:
        2D matrix representing the state of the game.
    output:
        2D matrix representing the updated state of the game.
    """
    return mat



import pygame
import numpy as np
from collections import Counter
def main():
    global M
    M = 8
    pygame.init()
    screen = pygame.display.set_mode((50*M, 50*M))
    pygame.display.set_caption('Interface of Five-in-a-Row')
    done = False
    pc_step = 0    
    mat=np.zeros((M,M),int)
    draw_board(screen, M)
    pygame.display.update()
    #mat[int(M/2)][int(M/2)]=1
    update_board(screen, mat)
    while not done:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                done=True
                
            if event.type!=pygame.QUIT:
                
                ###it is g12 turn
                mat=g12.update_by_pc(mat,c_param=2,r_param=2)
                ###
                
                
                update_board(screen, mat)
                #print("mat=",mat)
                done, _ = check_for_done(mat)
                if done:
                    print('winer is:',_)
                    break
                    
                    
                ### it is g3 turn
                mat = g3.update_by_pc(-1*mat)#transform to the result for g3 to put white stone
                ###
            
                mat=mat*(-1)
                done, _ = check_for_done(mat)
                #print('now mat is',mat,_)                
                #print('update2')
                # check for win or tie
                update_board(screen, mat)
                done, _ = check_for_done(mat)
                if done==True:
                    print('winer is:',_)
                    break

def main_noGUI_Ntimes(N=1000):
    global M
    winner_list1 = []
    g12r,g12c = 2,2
    g3r,g3c = 2,5
    for i in range(N):
        print(f"Starting iteration {i+1} of First {N}")
        M = 8
        done = False  
        mat=np.zeros((M,M),int)
        while not done:
            # g12 go first and then g3
            # print("After g3 update,mat is")
            # print(mat)
            mat=g12.update_by_pc(mat,r_param=g12r,c_param=g12c)
            done, winner = check_for_done(mat)
            if done==True:
                print('winer is:',winner)
                winner_list1.append(winner)
                break
            
            # print("After g12 update,mat is")
            # print(mat)
            # print()
            ### it is g3 turn
            mat = g3.update_by_pc(-1*mat,r_param=g3r,c_param=g3c) # transform to the result for g3 to put white stone
            mat=mat*(-1)
            # check for win or tie
            done, winner = check_for_done(mat)
            if done==True:
                print('winer is:',winner)
                winner_list1.append(winner)
                break

    winner_list2 = []
    for i in range(N):
        print(f"Starting iteration {i+1} of Second {N}")
        done = False 
        mat=np.zeros((M,M),int)
        while not done:
            # g3 go first and then g12
            # print("position 1")
            # print(mat)
            mat=g3.update_by_pc(mat,r_param=g3r,c_param=g3c)
            done, winner = check_for_done(mat)
            if done==True:
                print('winer is:',winner)
                winner_list2.append(winner)
                break
            
            # print("position 2")
            # print(mat)
            # print()
            mat = g12.update_by_pc(-1*mat,r_param=g12r,c_param=g12c) # transform to the result for g12 to put white stone
            mat=mat*(-1)
            # check for win or tie
            done, winner = check_for_done(mat)
            if done==True:
                print('winer is:',winner)
                winner_list2.append(winner)
                break
    print()
    print(f"g12 has parameter: r = {g12r},c = {g12c}")
    print(f"g3 has parameter: r = {g3r},c = {g3c}")
    print(f"winner_list1 is :{Counter(winner_list1)}(g12->g3)")
    print(f"winner_list2 is :{Counter(winner_list2)}(g3->g12)")

if __name__ == '__main__':
    # main()
    main_noGUI_Ntimes(N=100)
    
