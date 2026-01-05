import numpy as np
import random
import time
import sys
import itertools as itt
import copy


def create_empty_board():
    print("empty board")
    global board
    board = [[None for i in range(9)] for j in range(9)]

    global times
    times = {"update_candidates_time": 0, "sole_candidate_time": 0, "unique_candidate_time": 0, "sole_candidate_reducer_time": 0, "naked_subset_time": 0, "block_and_cr_time":0,"full_time":0,"unique_candidate_reducer_time":0,"init_time":0,"s_gen_time":0,"remove_init_time":0,"remove_cells_time":0}
    global full_time_start
    full_time_start = time.perf_counter()
    
    global board_coordinates
    board_coordinates = [(r,c,rc_to_box(r,c)) for r in range(9) for c in range(9)] #list of the row, column, and box coordinates for every cell

    global tries
    tries = 1

    global candidate_dict
    candidate_dict = {}

    time_start = time.perf_counter()
    init_coord_dict()
    init_related_cell_pairs()
    init_family_groups()

    times["init_time"] += time.perf_counter() - time_start

    return board

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


def remove_init(r_list,last_try):
    time_start = time.perf_counter()
    

    print('remove init')

    candidate_reducers = [sole_candidate_reducer,unique_candidate_reducer,naked_subset,block_and_cr]
    number_choosers = [sole_candidate,unique_candidate]
    strategies = {"candidate reducers":candidate_reducers,"number choosers": number_choosers}

    times["remove_init_time"] += time.perf_counter() - time_start

    if len(r_list[0]) == 2:
        r_list = [(r,c,rc_to_box(r,c)) for (r,c) in r_list]

    number_removed = remove_cells(strategies,r_list,last_try)
    if number_removed < len(r_list):
        try_again(r_list)
    else:
        end_print(True)
        return
    return

def end_print(success):
    times["full_time"] = time.perf_counter() - full_time_start
    if success == True:
        print("succesfully made sudoku")
    else:
        print("extra clues added")
    global tries
    print("tries: ",tries)
    for key, value in times.items():
        print(key, value*1000, "ms")

    for coord in board_coordinates:
        row,col,cell = coord
        if board[row][col] != None:
            print(board[row][col],end="")
        else:
            print(0,end="")
    print("")
    


def remove_cells(strategies, remove_list,last_try):
    failed_removes = 0
    number_removed = 0
    
    for coord in remove_list:
        time_start = time.perf_counter()
        target_row, target_col, target_box = coord

        #temporarily set current square to None to find out number of possible candidates
        temp = board[target_row][target_col]
        board[target_row][target_col] = None
        
        remove = False
        starting_candidate_lengths = []

        times["remove_cells_time"] += time.perf_counter() - time_start

        update_candidates()

        while [len(cands) for coord,cands in candidate_dict.items()] != starting_candidate_lengths:
            time_start = time.perf_counter()
            
            starting_candidate_lengths = [len(cell_candidates) for coord,cell_candidates in candidate_dict.items()]
            times["remove_cells_time"] += time.perf_counter() - time_start
            for strat in strategies["candidate reducers"]:
                strat()
            for strat2 in strategies["number choosers"]:
                if strat2(coord):
                    remove = True
                    break
            if remove:
                board[target_row][target_col] = None
                number_removed += 1
                break
            
        if not(remove):
            board[target_row][target_col] = temp
            print("unable to remove row: ",target_row,", col: ",target_col, " val: ",temp)
            for row in range(9):
                for (r,c,b) in board_coordinates:
                    if r == row:
                        print(candidate_dict[(r,c,b)],end="")
                print("")
            if not(last_try):
                return number_removed
            print_sudoku(board)
            print("*********")
            failed_removes += 1
    
    if failed_removes > 0:
        print("Can't remove any more")
        return number_removed

    print("Final\n")
    print_sudoku(board)
    print(candidate_dict)
    print("# removed",number_removed)
    return number_removed

def rc_to_box(row,col):
    box = (row//3)*3 + (col//3)
    box_cell = (row%3)*3 + (col%3)
    return box

def update_candidates(): #re-calculate possible candidates on the target cell
    time_start = time.perf_counter()

    for coord in board_coordinates:
        candidate_dict[coord] = set(range(1,10))


        
    for coord_a, coord_b in related_cell_pairs:
        if len(candidate_dict[coord_b]) > 1:
            row_a, col_a, box_a = coord_a
            candidate_dict[coord_b].discard(board[row_a][col_a])
        if len(candidate_dict[coord_a]) > 1:
            row_b, col_b, box_b = coord_b
            candidate_dict[coord_a].discard(board[row_b][col_b])
        
    times["update_candidates_time"] += time.perf_counter() - time_start
    return


def sole_candidate(target): #returns True if only 1 candidate for any targeted cells
    return len(candidate_dict[target]) == 1

def unique_candidate(target): #returns True if only one possible position for a given number
    time_start = time.perf_counter()

    coord_groups = (coord_dict[target]["row"],coord_dict[target]["col"],coord_dict[target]["box"])

    for coord_group in coord_groups:
        related_candidates = set()
        [related_candidates.update(candidate_dict[coord]) for coord in coord_group]
        
        u_candidates = candidate_dict[target] - related_candidates

        if len(u_candidates) == 1:
            times["unique_candidate_time"] += time.perf_counter() - time_start
            return u_candidates.pop()

    times["unique_candidate_time"] += time.perf_counter() - time_start
    return False
        
def sole_candidate_reducer(): #removes matching candidates in cells related to a cell with a sole candidate
    time_start = time.perf_counter()

    for coord in board_coordinates:
        if sole_candidate(coord):
            (single_candidate,) = candidate_dict[coord]
            family_cells = coord_dict[coord]["all"] #getting related cells not including the target cell
            [candidate_dict[cur_coord].discard(single_candidate) for cur_coord in family_cells] #filter to family cells that contain the single candidate

    times["sole_candidate_reducer_time"] += time.perf_counter() - time_start
    return

def unique_candidate_reducer(): #removes matching candidates in cells related to a cell with a sole candidate
    time_start = time.perf_counter()
    for coord in board_coordinates:
        times["unique_candidate_reducer_time"] += time.perf_counter() - time_start

        uc_value = unique_candidate(coord)
        time_start = time.perf_counter()

        if uc_value:
            family = coord_dict[coord]["all"]
            [candidate_dict[coord].discard(uc_value) for coord in family]
            candidate_dict[coord] = {uc_value}
    times["unique_candidate_reducer_time"] += time.perf_counter() - time_start


        
def naked_subset(): #if n squares have the same n candidates and only those candidates, remove those candidates from all other squares in that family
    time_start = time.perf_counter()

    for group in family_groups:
        _2_cand_coords = [coord for coord in group if len(candidate_dict[coord])==2]
        for coord1, coord2 in itt.combinations(_2_cand_coords,2): #every combination of 2 cells in the temp group
            if (candidate_dict[coord1] == candidate_dict[coord2]) and (len(candidate_dict[coord1]) == 2): #if the candidates of two cells equal each other and are of length 2
                naked_subset_candidates = candidate_dict[coord1]
                related_cells = [coord for coord in group if ((coord != coord1) and (coord != coord2))] #every cell in the group, not including the naked subset cells
                [candidate_dict[coord].difference_update(naked_subset_candidates) for coord in related_cells]

        _3_cand_coords = [coord for coord in group if 2<=len(candidate_dict[coord])<=3]
        for coord1, coord2, coord3 in itt.combinations(_3_cand_coords,3):
            naked_subset_candidates = candidate_dict[coord1] | candidate_dict[coord2] | candidate_dict[coord3]
            if len(naked_subset_candidates) == 3:
                related_cells = [coord for coord in group if ((coord != coord1) and (coord != coord2) and (coord != coord3))] #every cell in the group, not including the naked subset cells
                [candidate_dict[coord].difference_update(naked_subset_candidates) for coord in related_cells]

    times["naked_subset_time"] += time.perf_counter() - time_start

def block_and_cr(): #if only candidate locations in a box is in 1 row/col, remove that canddidate from the cells in that row/col outside the box
    start_time = time.perf_counter()
    for box in range(9):
        box_coords = set([(r,c,b) for r,c,b in board_coordinates if b == box])
        in_group_candidates, out_group_candidates = set(), set()
        for group_type, group_num in itt.product(range(2),range(3)):
            in_group_coords = [(r,c,b) for r,c,b in box_coords if (r,c,b)[group_type]%3==group_num]
            out_group_coords = box_coords - set(in_group_coords)

            [in_group_candidates.update(candidate_dict[coord]) for coord in in_group_coords]
            [out_group_candidates.update(candidate_dict[coord]) for coord in out_group_coords]

            target_candidate_values = in_group_candidates-out_group_candidates

            if len(target_candidate_values) > 0:
                #create remove_group, which is the coordinates of cells on the specific row or column, not including the target box
                remove_group_index = in_group_coords[0][group_type]
                remove_group = [(r,c,b) for r,c,b in board_coordinates if (r,c,b)[group_type] == remove_group_index]
                [remove_group.remove(coord) for coord in in_group_coords]

                for coord in remove_group:
                    [candidate_dict[coord].discard(candidate) for candidate in target_candidate_values]
    times["block_and_cr_time"] += time.perf_counter() - start_time
        

def init_coord_dict(): #creates dict of all related cells not including the target cell
    global coord_dict
    coord_dict = {}
    for coord in board_coordinates:
        target_row, target_col, target_box = coord
        coord_dict[coord] = {}
        coord_dict[coord]["row"] = set([(r,c,b) for r,c,b in board_coordinates if ((r==target_row) and (coord!=(r,c,b)))])
        coord_dict[coord]["col"] = set([(r,c,b) for r,c,b in board_coordinates if ((c==target_col) and (coord!=(r,c,b)))])
        coord_dict[coord]["box"] = set([(r,c,b) for r,c,b in board_coordinates if ((b==target_box) and (coord!=(r,c,b)))])
        coord_dict[coord]["all"] = coord_dict[coord]["row"].union(coord_dict[coord]["col"]).union(coord_dict[coord]["box"])


def init_related_cell_pairs():
    global related_cell_pairs
    related_cell_pairs = set()

    for key, coords in coord_dict.items():
        [related_cell_pairs.add(frozenset((key,coord))) for coord in coords["all"]]

def init_family_groups():
    global family_groups
    family_groups = [[] for i in range(27)]
    for group_type in range(3):
        for coord in board_coordinates:
            group_num = coord[group_type] + group_type*9
            family_groups[group_num].append(coord)
    family_groups = tuple([tuple(group) for group in family_groups])


def get_current_board():
    return board

def try_again(r_list):
    global tries

    max_tries = 450
    
    if tries < max_tries:
        print("try again. try # ",tries)
        tries += 1
        s_gen()
        remove_init(r_list, tries==max_tries)
    else:
        end_print(False)




