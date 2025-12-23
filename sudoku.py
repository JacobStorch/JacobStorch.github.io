import numpy as np
import random
import time
import sys
import itertools as itt

global board
board = [[None for i in range(9)] for j in range(9)]


def s_gen():

    global rows, cols, boxes, board
    
    rows = [[None for i in range(9)] for j in range(9)]
    rows[0] = random.sample(range(1, 10), k=9) #start with first row randomly generated
    board = rows
    exclude = [[set() for i in range(9)] for j in range(9)]
    #print(rows)

    cols = [[lambda y=x,x=y: rows[y][x] for x in range(9)] for y in range(9)] #link columns to rows
    boxes = [[lambda y=(x//3)+(y//3)*3, x=x%3+(y%3)*3: rows[y][x] for x in range(9)] for y in range(9)]

    #print("cols:", [[func() for func in i] for i in cols])

    row = 1 #start at second row
    col = 0
    exclude_last = 0 #don't exclude the last square for 1st square we generate
    while row <= 8:
        while col <= 8:
            box = (col//3)+(row//3)*3
            
            last_square = rows[row][col]
            rows[row][col] = None #make sure the current square is empty

            #print()
            #[print(row) for row in rows]
            if col==0:
                last_col = 8
                last_row = row - 1
            else:
                last_col = col - 1
                last_row = row

            cur_exclude = [[i for i in rows[row]] + [func() for func in cols[col]] + [func() for func in boxes[box]] + [last_square] * exclude_last]
            cur_exclude = cur_exclude[0]
            exclude[row][col].update(cur_exclude)
            cur_exclude = exclude[row][col]
            allowed_numbers = [i for i in range(1,10) if i not in cur_exclude]

            #print("exclude",cur_exclude)
            #print("include",allowed_numbers)
            #print("----------")

            if len(allowed_numbers) == 0: #if no valid digits left
                exclude_last = 1 #exclude the last square
                exclude[row][col] = set()
                col = last_col # go back to last square
                row = last_row

            else:
                exclude_last = 0 #don't exclude last square
                rows[row][col] = random.choice(allowed_numbers)
                col += 1 #go to next square

        col = 0
        row+=1
            
            

    print_sudoku(board)
    #print("cols:", [[func() for func in i] for i in cols])
    #print("boxes:", [[func() for func in i] for i in boxes])

def print_sudoku(board): #gptd
    for row_index, row in enumerate(board):
        # Format each row into groups of 3 for better readability
        formatted_row = " | ".join(
            " ".join(str(cell) if cell is not None else "." for cell in row[i:i+3])
            for i in range(0, 9, 3)
        )
        print(formatted_row)
        
        # Add horizontal dividers every 3 rows
        if row_index % 3 == 2 and row_index != 8:
            print("-" * 21)


def remove_init(r_count):

    global candidates
    global candidate_cols, candidate_boxes
    global board_coordinates
    candidates = [[set([board[row][col]]) for col in range(9)] for row in range(9)]
    candidate_cols = [[lambda y=x,x=y: candidates[y][x] for x in range(9)] for y in range(9)] #link columns to rows
    candidate_boxes = [[lambda y=(x//3)+(y//3)*3, x=x%3+(y%3)*3: candidates[y][x] for x in range(9)] for y in range(9)] #links boxes to rows
    board_coordinates = [[r,c,rc_to_box(r,c)['box']] for r in range(9) for c in range(9)] #list of the row, column, and box coordinates for every cell


    print('remove init')

    candidate_reducers = [sole_candidate_reducer,naked_subset]
    number_choosers = [sole_candidate,unique_candidate]
    strategies = {"candidate reducers":candidate_reducers,"number choosers": number_choosers}

    r_count = int(r_count)
    remove_cells(strategies,r_count)


def remove_cells(strategies, remove_count,iterations=0):
    removeable_cells = [[row,col] for row in range(9) for col in range(9) if board[row][col] != None] #a cell is removeable if it isn't None
    numbers_removed = 81 - len(removeable_cells)
    blank_cells = []
    starting_numbers_removed = numbers_removed


    while numbers_removed < remove_count:
        iterations += 1

        if len(removeable_cells) == 0:
            #re-run remove cells if there have been more numbers removed since the start of the function
            board_change = (starting_numbers_removed != numbers_removed)
            if board_change:
                print("re-calling function")
                numbers_removed = remove_cells(strategies, remove_count)
            else:
                print("Can't remove any more")
                print(candidates)
            break
        
        #set the target row and column, and remove that row column combo from future removeable cells
        target_cell_num = random.randint(0,len(removeable_cells)-1)
        target_row, target_col = removeable_cells[target_cell_num]
        target_box = rc_to_box(target_row,target_col)['box']
        del removeable_cells[target_cell_num]
        target = [[target_row, target_col, target_box]]

        #temporarily set current square to None to find out number of possible candidates
        temp = board[target_row][target_col]
        board[target_row][target_col] = None
        remove = False


        update_candidates(board_coordinates)

        for strat in strategies["candidate reducers"]: #remove excess candidates
            strat()
        
        for strat in strategies["number choosers"]:
            if strat(target) and one_solution_check(target, temp, numbers_removed): #if the strategy returns true
                remove = True
                break #only use one strategy if it returns true
        
        if not(remove):
            board[target_row][target_col] = temp
        elif remove:
            board[target_row][target_col] = None
            blank_cells.append([target_row,target_col])
            target_cell_num=0
            numbers_removed += 1
            print("**************************")
            print_sudoku(board)
            print("# removed", numbers_removed)
            print("rc",target_row,target_col)

    print("Final\n")
    print_sudoku(board)
    print(candidates)
    print("# removed",numbers_removed)
    return numbers_removed

def rc_to_box(row,col):
    box = (row//3)*3 + (col//3)
    box_cell = (row%3)*3 + (col%3)
    return {"box":box,"box_cell":box_cell}

def box_to_rc(box,box_cell):
    row = (box//3)*3 + (box_cell//3)
    col = (box%3)*3 + (box_cell%3)
    return {"row":row,"col":col}

def update_candidates(targets): #re-calculate possible candidates on the target cell
    print("pre-update_candidates",candidates)
    for target in targets:
        target_row, target_col, target_box = target
        candidates[target_row][target_col] = set([i for i in range(1,10)])
        related_cell_coords = get_family([target])
        for coord in related_cell_coords: #for coordinate in all related cell coordinates
            cur_row,cur_col,cur_box = coord
            if ([cur_row, cur_col] != [target_row, target_col]): #if the current cell is different than the target cell
                if board[cur_row][cur_col] in candidates[target_row][target_col]: #if the current cell value is in the target candidates
                    candidates[target_row][target_col].remove(board[cur_row][cur_col]) #remove that value from the target candidates
    print("post-update_candidates",candidates)
    print("----------------")
    return


def sole_candidate(targets): #returns True if only 1 candidate for any targeted cells
    for target in targets:
        print("sc0")
        target_row, target_col, target_box = target
        if len(candidates[target_row][target_col]) == 1:
            print("sole candidate returning true at row ",target_row,", col ",target_col)
            print("candidates for ref:",candidates)
            print("----------------")
            return True

    return False

def unique_candidate(targets): #returns True if only one possible position for a given number
    print("uc",targets)
    print(candidates)
    print('-------------')
    for target in targets:
        row, col, box = target
        temp = board[row][col]
        board[row][col] = None #temporarily set the current cell to none
        #update candidates for every cell

        family_candidates = set() #candidates in same row, column, or box

        for cur_col in range(len(candidates)):
            if cur_col != col:
                family_candidates.union(candidates[row][cur_col]) #adds all candidates in row to rcb_candidates
        u_row_candidate = candidates[row][col] - family_candidates

        for cur_row in range(len(candidates)):
            if cur_row != row:
                family_candidates = set(candidates[cur_row][col]) #adds all candidates in col to rcb_candidates
        u_col_candidate = candidates[row][col] - family_candidates

        for cur_cell in range(len(candidates)):
            if cur_cell != rc_to_box(row,col)["box_cell"]:
                u_candidate = set(candidate_boxes[cur_cell]) #adds all candidates in box to rcb_candidates
        u_box_candidate = candidates[row][col] - family_candidates

        if len(u_candidate) == 1:
            print("UNIQUE CANDIDATE")
            print_sudoku(board)
            print(candidates)
            print("unique candidate:",u_candidate,"r,c",row,col)
            return True
        
def sole_candidate_reducer(): #removes matching candidates in cells related to a cell with a sole candidate
    print("pre-SCR candidates,",candidates)
    for target in board_coordinates:
        target_row, target_col, target_box = target
        if len(candidates[target_row][target_col]) == 1:
            (single_candidate,) = candidates[target_row][target_col]
            family_cells = get_family([target])
            for cur_row,cur_col,cur_box in family_cells:
                if (single_candidate in candidates[cur_row][cur_col]) and ([cur_row,cur_col] != [target_row, target_col]): #if the current cell is not the target cell, and the target candidate is present
                    print("checkpoint SCR2")
                    print('target row ',target_row,', target col ',target_col)
                    print('cur row ',cur_row,', cur col ',cur_col)
                    candidates[cur_row][cur_col].remove(single_candidate)
                    
                    print('post candidates',candidates)
                    print('*******************')
    print("post-SCR candidates",candidates)
    return


        
def naked_subset(): #if n squares have the same n candidates and only those candidates, remove those candidates from all other squares
    #check every row, column, box for duplicate candidates
    for group_type, group_num in itt.product(range(3), range(9)): #group_type refers to row, column, or box. Group num is the group's index
        twin_candidates_coords = []
        temp_group = [coord for coord in board_coordinates if coord[group_type] == group_num] #the current row, col, or box
        for i, j in itt.combinations(range(9),2): #every combination of 2 cells in the temp group
            row1,col1,box1 = temp_group[i]
            row2,col2,box2 = temp_group[j]
            if (candidates[row1][col1] == candidates[row2][col2]) and (len(candidates[row1][col1]) == 2): #if the candidates of two cells equal each other and are of length 2
                print("ns1")
                print("pre candidates",candidates)
                print("board_coordinates", temp_group[i],temp_group[j])
                print('temp group',temp_group)
                print('group type ',group_type,', group num ',group_num)
                naked_subset_candidates = candidates[row1][col1]
                for coord in temp_group:
                    if (coord!=temp_group[i]) and (coord!=temp_group[j]): #for every cell in the group, not including the naked subset cells
                        cur_row, cur_col, cur_box = coord
                        print("ns checkpoint 2")
                        [candidates[cur_row][cur_col].remove(candidate) for candidate in naked_subset_candidates if candidate in candidates[cur_row][cur_col]]
                        print('post candidates',candidates)
                        print('---------------')


    return
        


            


def get_family(targets):
    related_cells = set()
    for target in targets:
        #get the row, col, and box of the current cell
        row, col, box = target
        #add all cells in the same row, box, or column to the related_cells set
        for coordinate in board_coordinates:
            cur_row,cur_col,cur_box=coordinate
            if (cur_row==row) or (cur_col==col) or (cur_box==box):
                related_cells.add(tuple(coordinate))
    return related_cells

            


        
def one_solution_check(target, temp, numbers_removed): #makes sure the sudoku only has one solution
    print("OSC. Target: ",target)
    print(candidates)
    [[row,col,box]] = target
    if numbers_removed == 0: #we know there is only one solution if this is the first cell removed
        return True
    
    #below ensures that there exists an empty cell that is not the target with only one possible candidate
    board[row][col] = temp
    for row in range(len(rows)):
        for col in range(len(cols)):
            if board[row][col] == None:
                if len(candidates[row][col]) == 1:
                    print("OSC checkpoint 2")
                    return True
    
    return False

def get_current_board():
    return board



