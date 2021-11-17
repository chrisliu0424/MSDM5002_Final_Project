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

# Check for done function by TQW
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

    size = mat.shape[0]
    for i in range(size-5+1):
        for j in range(size-5+1):
            #print(self.board[i:i+5,j:j+5])
            res = _five_mat_res(mat[i:i+5,j:j+5])
            if res == None:
                continue
            else:
                return True, res
    if np.all(mat != 0):
        return True, 0
    return False,0

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


# =============================================================================
# # Check for done function written by Chris on Nov.11
# # Using the difference of last_mat and mat to find the last position, and determine only by the relative 
# ######################################## This check_for_done is 3 times faster than the standard one ############################################################
# def check_for_done(mat):
#     global last_mat
#     # global except_times
#     # global check_times
# 
#     # print("check_times inside function is:",check_times)
#     # check_times+=1
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
#         print("into try")
#         # Check if horizontal made 5 connects
#         temp_left = left
#         while temp_left+4<=right:
#             if np.sum(mat[row,temp_left:temp_left+5]) == 5*player:
#                 return True,player
#             temp_left+=1
# 
#         # Check for the vertical
#         temp_top = top
#         while temp_top+4<=bottom:
#             if np.sum(mat[temp_top:temp_top+5,col]) == 5*player:
#                 return True,player
#             temp_top+=1
# 
#         # # Check for the diagonal
#         temp_left = left
#         temp_top = top
#         while temp_left+4<=right and temp_top+4<=bottom:
#             if(np.sum(mat[temp_top:temp_top+5,temp_left:temp_left+5].diagonal())==5*player):
#                 return True,player
#             temp_left+=1
#             temp_top+=1
# 
#         # Check for the off-diagonal
#         temp_col = col
#         temp_row = row
#         while temp_col<=7 and temp_row>=0:
#             if(np.sum(np.fliplr(mat[temp_row:temp_row+5,temp_col-4:temp_col+1]).diagonal())==5*player):
#                 return True,player
#             temp_col+=1
#             temp_row-=1
#         if np.sum(mat==0)==0:
#             return True,0
#         else:
#             return False,0
# 
#     except:                             # if last_map not even exist, this is the first step
#         print("get into the exception")
#         # except_times+=1
#         last_mat = mat.copy()
#         # search_lst=[(2,2),(2,3),(2,4),(2,5),
#         #         (3,2),(3,3),(3,4),(3,5),
#         #         (4,2),(4,3),(4,4),(4,5),
#         #         (5,2),(5,3),(5,4),(5,5)]
#         # for (i,j) in search_lst:
#         #     for x in range(i-2,i+3):                  #窗口内横排即将5连
#         #         if sum(mat[x][j-2:j+3])==5:   
#         #             return True, 1
#         #         elif sum(mat[x][j-2:j+3])==-5:
#         #             return True, -1
#         #     for y in range(j-2,j+3):                  #窗口内竖列即将5连
#         #         if mat[i-2][y]+mat[i-1][y]+mat[i][y]+mat[i+1][y]+mat[i+2][y]==5:   
#         #             return True,1
#         #         elif mat[i-2][y]+mat[i-1][y]+mat[i][y]+mat[i+1][y]+mat[i+2][y]==-5:
#         #             return True,-1 
#         #     dia_z,dia_f=0,0
#         #     for n in range(5):
#         #         dia_z+=mat[i-2+n][j-2+n]    #主对角线（左上到右下）即将5连
#         #         dia_f+=mat[i+2-n][j-2+n]    #副对角线（左下到右上）即将5连
#         #     if dia_z==5 or dia_f==5:
#         #         return True,1                           #最终返回A则1将在下一步胜
#         #     elif dia_z==-5 or dia_f==-5:
#         #         return True,-1                        #最终返回B则-1将在下一步胜                                        
#         # else:
#         #     if (mat==0).sum()==0:                   #如果棋盘没有位置是空的，返回结束，平
#         #         return True,0
#         #     else:
#         #          return False,0                       #最终返回C则没有人会在下一步获得胜利
#         size = mat.shape[0]
#         if np.sum([mat==0]) > (size*size-9):     # if less than 9 moves, no winner
#             return False,0
# 
#         mat1 = mat.copy()
#         mat1[mat1==-1] = 0                 # mat1 only keeps 1 in the mat
#         mat2 = mat.copy()
#         mat2[mat1==1] = 0
#         mat2 = mat2*(-1)                   # mat2 only keeps -1 in the mat, but convert all -1 to 1 for future calculation
#         
#         rowsum = np.sum(mat1, 0)
#         colsum = np.sum(mat1,1)
#         row_to_check=[index for index,value in enumerate(rowsum) if value>4]
#         col_to_check=[index for index,value in enumerate(colsum) if value>4]
# 
#         rowsum2 = np.sum(mat2,0)
#         colsum2 = np.sum(mat2,1)
#         row_to_check2 = [index for index,value in enumerate(rowsum2) if value>4]
#         col_to_check2 = [index for index,value in enumerate(colsum2) if value>4]
# 
#         for row in row_to_check:
#             for col_index in range(0,size-4):
#                 if np.sum(mat1[row,col_index:col_index+5]) == 5:
#                     return True,1
#         for col in col_to_check:
#             for row_index in range(0,size-4):
#                 if np.sum(mat1[row_index:row_index+5,col]) == 5:
#                     return True,1 
#         
#         for row in row_to_check2:
#             for col_index in range(0,size-4):
#                 if np.sum(mat2[row,col_index:col_index+5]) == 5:
#                     return True,-1
#         for col in col_to_check2:
#             for row_index in range(0,size-4):
#                 if np.sum(mat2[row_index:row_index+5,col]) == 5:
#                     return True,-1 
# 
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
#     
# =============================================================================
