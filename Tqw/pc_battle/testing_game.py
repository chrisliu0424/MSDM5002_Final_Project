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


    if (diag_sum_tl == -5) or (diag_sum_tl == -5):
        return -1

    # if not over - no result
    return None


# Check for done function written by Chris on Nov.11
# Using the difference of last_mat and mat to find the last position, and determine only by the relative 
#### This check_for_done is 4 times faster than the standard one ######################
def check_for_done(mat):
    global last_mat
    try:
        if len((np.where(abs(mat-last_mat)==1))[0])!=1:
            last_mat = mat.copy()
            #print(tt)                   # manually get into the exception clause
        pos=[int(x) for x in np.where(abs(mat-last_mat)==1)]
        last_mat = mat.copy()
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

    except:                             # if last_map not even exist, this is the first step
    
        # print("get into the exception")              # debug message
        # if last_mat does not exist or does not match condition, we perpare this mat to be last_mat as we call next time
        last_mat = mat.copy()           
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
    #return done,result

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
                mat=g12.update_by_pc(mat)
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


if __name__ == '__main__':
    main()
    
