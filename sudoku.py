import numpy as np
import random
import time
import sys

from flask import Flask, render_template, jsonify

app = Flask(__name__)



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
    candidates = [[[] for i in range(9)] for j in range(9)]
    candidate_cols = [[lambda y=x,x=y: candidates[y][x] for x in range(9)] for y in range(9)] #link columns to rows
    candidate_boxes = [[lambda y=(x//3)+(y//3)*3, x=x%3+(y%3)*3: candidates[y][x] for x in range(9)] for y in range(9)]


    print('remove')
    strategies = [sole_candidate,unique_candidate]
    remove_cells(strategies,r_count)


def remove_cells(strategies, remove_count):
    i = 0
    it_count = 0
    remove_cells = [[i,j] for i in range(9) for j in range(9)]
    target_cell_num = 0
    while i < remove_count:
        it_count+=1

        if target_cell_num >= 81:
            print("Can't remove any more")
            print(candidates)
            break


        #r_row = random.randint(0,8)
        #r_col = random.randint(0,8)


        [r_row, r_col] = remove_cells[target_cell_num]
        target_cell_num+=1



        if board[r_row][r_col] == None:
            continue

        remove = False
        for strat in strategies:
            if strat(r_row, r_col):
                remove = True
        
        if remove:
            board[r_row][r_col] = None
            target_cell_num=0
            i+=1
    print_sudoku(board)

def strat_init(row, col):
    box = (col//3)+(row//3)*3
    #print(board, row, col)
    cell_val = board[row][col]
    board[row][col] = None
    

    cur_exclude = set([[i for i in rows[row]] + [func() for func in cols[col]] + [func() for func in boxes[box]]][0])
    allowed_numbers = [i for i in range(1,10) if i not in cur_exclude]

def rc_to_box(row,col):
    box = (row//3)*3 + (col//3)
    box_cell = (row%3)*3 + (col%3)
    return {"box":box,"box_cell":box_cell}

def box_to_rc(box,box_cell):
    row = (box//3)*3 + (box_cell//3)
    col = (box%3)*3 + (box_cell%3)
    return {"row":row,"col":col}



def reduce_candidates():
    #box/row combo
    for box in range(len(candidate_boxes)):
        for digit in range(1,10):
            #count how many times each digit appears in the candidate list for each row
            can_locations = [1 for can_list in candidate_boxes[box] if digit in can_list]
            if sum(can_locations) == 2:
                locations = [i for i in range(9) if digit in candidate_boxes[box][i]]
                if locations[0]//3==locations[1]//3:
                    row = (box//3)*3+locations[0]//3
                    for square in candidates[row]:
                        if square not in locations:
                            candidates[row] = [sq for sq in candidates[row] if sq != digit]


def update_sole_candidates(row, col): #updates the possible candidates for a given cell
    box = (col//3)+(row//3)*3
    #print(board, row, col)
    cell_val = board[row][col]
    board[row][col] = None
    cur_exclude = set([[i for i in rows[row]] + [func() for func in cols[col]] + [func() for func in boxes[box]]][0])
    cell_candidates = [i for i in range(1,10) if i not in cur_exclude]
    board[row][col] = cell_val

    return set(cell_candidates)


def sole_candidate(row, col):#returns True if only 1 candidate for given cell
    reduce_candidates
    c_candidates = update_sole_candidates(row, col)

    return len(c_candidates)==1

def unique_candidate(row, col):
    temp = board[row][col]
    board[row][col] = None #temporarily set the current cell to none
    #update candidates for every cell
    box = rc_to_box(row,col)["box"]
    # print("xxxx")
    # print(row,col)
    # print(rc_to_box(row,col)["box_cell"])

    for temp_row in range(len(rows)):
        for temp_col in range(len(cols)):
            candidates[temp_row][temp_col] = update_sole_candidates(temp_row, temp_col)

    rcb_candidates = set()

    for cur_col in range(len(candidates)):
        if cur_col != col:
            rcb_candidates.update(candidates[row][cur_col])#adds all candidates in row to rcb_candidates

    for cur_row in range(len(candidates)):
        if cur_row != row:
             rcb_candidates.update(candidates[cur_row][col])#adds all candidates in row to rcb_candidates

    for cur_cell in range(len(candidates)):
        if cur_cell != rc_to_box(row,col)["box_cell"]:
            rcb_candidates.update(candidate_boxes[cur_cell])#adds all candidates in box to rcb_candidates

    u_candidate= candidates[row][col] - rcb_candidates
    board[row][col] = temp #set the target cell back to original value
    if len(u_candidate)==1:
        # print('----------------')
        # print_sudoku(rows)
        # for can in candidates:
        #     print(can)
        # print(u_candidate,"(",row,col,")")
        # print('rcb',rcb_candidates)
        return True


             




s_gen()



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get-board")
def get_board():
    return jsonify(board)

if __name__ == "__main__":
    app.run(debug=True)
