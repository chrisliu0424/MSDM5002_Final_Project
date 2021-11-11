# 2021.11.06
# Chris L
# Writing the classes needed for project

##### TODO:
##### 1. check_for_done function is wrong
##### 2. check the correctness of the best_UCB function
##### 3. check the correctness of the roll-out function
##### 4. optimize expand function, to only expand on nearby positions(9*9)
##### 5. add artificial spot to drop the chess


import time
import numpy as np
import pygame

########################################  functions for the GUI DON'T TOUCH   ########################################
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

def update_by_pc(mat):
    """
    This is the core of the game. Write your code to give the computer the intelligence to play a Five-in-a-Row game 
    with a human
    input:
        2D matrix representing the state of the game.
    output:
        2D matrix representing the updated state of the game.
    """
    node = Node(mat=mat)
    next_node = monte_carlo_tree_search(node)
    return next_node.state

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

################################################ END FOR GUI ################################################

################################################ START MCTS ################################################
def monte_carlo_tree_search(root):
    start = time.time()
    computation_time=1
    i=0
    while time.time()-start<computation_time:
        leaf = traverse(root) # leaf = unvisited node 
        simulation_result = rollout(leaf)
        expand(leaf)
        backpropagate(leaf, simulation_result)
        i+=1
    print(f"Total {i} simulations done in {computation_time}s")
    return best_child(root)

def expand(node):
    for pos in node.possible_positions:
        temp_node = Node(mat = update_state(node.state,pos,parent_is_npc=node.is_npc),parent = node)
        temp_node.update_parents_child()
    return

# For the traverse function, to avoid using up too much time or resources, you may start considering only 
# a subset of children (e.g 5 children). Increase this number or by choosing this subset smartly later.
def traverse(node):
    while len(node.children)>0:
        node = best_UCB(node)
    return node # in case no children are present / node is terminal 
                                                 
def rollout(node):
    while not node.is_terminal:
        node = rollout_policy(node)
    _,winner = check_for_done(node.state)
    return winner 

def rollout_policy(node):
    drop_pos = node.possible_positions[np.random.choice(len(node.possible_positions))]
    new_node = Node(mat = update_state(mat=node.state,pos=drop_pos,parent_is_npc = node.is_npc),parent = node)
    return new_node

def update_stats(node,winner):
    if (winner == -1) and (node.is_npc == True):
            node.win+=1
    elif winner == 1:
        if node.is_npc == False:
            node.win+=1
    node.visits+=1

def backpropagate(node, result):
    if not node:
        return 
    node.stats = update_stats(node, result) 
    backpropagate(node = node.parent,result = result)

def best_child(node):
    #pick child with highest number of visits   
    return best_UCB(node)


######################################## END FOR MCTS ################################################

######################################## START FOR NODE CLASS ########################################
def generate_remaining(mat):
    """
    Find all empty position in the board
    return a list of tuples with [(row1,col1),(row2,col2),...]
    """
    available_positions = []
    for row in range(len(mat)):
        for col in range(len(mat)):
            if mat[row,col]==0:
                available_positions.append((row,col))
    return available_positions

def UCB(node,c=2):
    """"
    return the UCB value for the current node, with a adjustable parameter c = 2 as default.
    c is the bias parameter
    """
    w = node.win
    ni = node.visits
    n_parent = node.parent.visits
    return (w/ni+c*np.sqrt(np.log(n_parent/ni))) if ni!=0 else np.Inf

def best_UCB(node):
    """
    Find the child node with maximum UCB value in the current node.
    """
    return node.children[np.argmax([UCB(temp_node,c=2) for temp_node in node.children])]

def update_state(mat,pos,parent_is_npc = False):
    """
    temperary function to drop the chess
    """
    # print("call to update state")
    # print(f"pos is{pos}")
    temp_mat = mat.copy()
    if parent_is_npc==True:                # if parent is NPC, then now we drop the 1, else drop -1 indicating NPC
        temp_mat[pos] = 1
    else:
        temp_mat[pos] = -1
    return temp_mat

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
    search_lst=[(2,2),(2,3),(2,4),(2,5),
                (3,2),(3,3),(3,4),(3,5),
                (4,2),(4,3),(4,4),(4,5),
                (5,2),(5,3),(5,4),(5,5)]
    for (i,j) in search_lst:
        for x in range(i-2,i+3):                  #窗口内横排即将5连
            if sum(mat[x][j-2:j+3])==5:   
                return True, 1
            elif sum(mat[x][j-2:j+3])==-5:
                return True, -1
        for y in range(j-2,j+3):                  #窗口内竖列即将5连
            if mat[i-2][y]+mat[i-1][y]+mat[i][y]+mat[i+1][y]+mat[i+2][y]==5:   
                return True,1
            elif mat[i-2][y]+mat[i-1][y]+mat[i][y]+mat[i+1][y]+mat[i+2][y]==-5:
                return True,-1 
        dia_z,dia_f=0,0
        for n in range(5):
            dia_z+=mat[i-2+n][j-2+n]    #主对角线（左上到右下）即将5连
            dia_f+=mat[i+2-n][j-2+n]    #副对角线（左下到右上）即将5连
        if dia_z==5 or dia_f==5:
            return True,1                           #最终返回A则1将在下一步胜
        elif dia_z==-5 or dia_f==-5:
            return True,-1                        #最终返回B则-1将在下一步胜
        elif (mat==0).sum()==0:
            return True,0                        #如果棋盘没有位置是空的，返回结束，平
        return False,0                       #最终返回C则没有人会在下一步获得胜利

class Node():
    def __init__(self,mat=np.zeros([8,8]),parent=None):
        self.state = mat                               # state of the current node
        self.parent = parent                           # record the parent of the current node
        self.children = []                             # create an empty list to record all the children
        done,_ = check_for_done(mat)                   # check if the matrix has a result
        if done == True:                             
            self.is_terminal = True                    # set is_terminal to True if the game has been terminated
        else:
            self.is_terminal = False
        self.win = 0                                   # record the number of wins in the current node
        self.visits = 0                                # record the number of total visits in the current node
        self.possible_positions = generate_remaining(self.state)             # find all the possible positions in the current state 
        if self.parent is None:                        # record if the node is myself(npc, white) or for my opponent(user, black) 
            self.is_npc = False
        elif self.parent.is_npc == False:
                self.is_npc = True
        else:
            self.is_npc = False

    def update_parents_child(self):
        """
        if a new child is created, add this node to his parent's children attribute
        input the current child node, it will automatically be added to his parent node's children attribute
        """
        self.parent.children.append(self)

if __name__ == '__main__':
    
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
                done,winner = check_for_done(mat)
                # print message if game finished
                if done == True:
                    print(f"The game is done, winner is {winner}")
                    break
                # otherwise continue
                
                mat = update_by_pc(mat)
                render(screen,mat)
                # check for win or tie
                done,winner = check_for_done(mat)
                # print message if game finished
                if done == True:
                    print(f"The game is done, winner is {winner}")
                    break
                    # otherwise contibue
    pygame.quit()
    