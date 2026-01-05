document.addEventListener("DOMContentLoaded", function () {
    start_up();

    // New Game
    document.getElementById("new-game").addEventListener("click", function () {
        fetch("/start_up", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                updateGameBoard(data.board);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    document.getElementById("premade-house").addEventListener("click", function () {
        const preset_cells = [
        [0,0],[0,1],[0, 4],[0,8],
        [1,3],[1,4],[1, 5],[1,8],
        [2,2],[2,3],[2,5],[2,6],
        [3,1],[3,2],[3,6],[3,7],
        [4,0],[4,1],[4, 3],[4,5],[4,7],[4,8],
        [5,1],[5,3],[5,5],[5,7],
        [6,1],[6,7],
        [7, 1],[7,3],[7,5],[7,7],
        [8, 1],[8,3],[8,7]
    ];
    
    premade_setup(preset_cells)
    })

    document.getElementById("premade-stripes").addEventListener("click", function () {
        const preset_cells = [[0,0],[0,3],[0,6],[1,1],[1,4],[1,7],[2,2],[2,5],[2,8],[3,0],[3,3],[3,6],[4,1],[4,4],[4,7],[5,2],[5,5],[5,8],[6,0],[6,3],[6,6],[7,1],[7,4],[7,7],[8,2],[8,5],[8,8]];

        premade_setup(preset_cells)
    })

    // Click cell
    document.querySelectorAll('.sudoku-cell').forEach(cell => {
      cell.addEventListener('click', () => {
        cell.classList.toggle('selected');
      });
    });

    // Create Board
    document.getElementById("create-board").addEventListener("click", function () {
        
        let all_cells_arr = []
        const all_cells = document.querySelectorAll(".sudoku-cell");
        all_cells.forEach(cell => {
            all_cells_arr.push([Number(cell.dataset.row), Number(cell.dataset.col)])
        });
        
        let keep_cells = []
        const selected_cells = document.querySelectorAll(".sudoku-cell.selected");
        selected_cells.forEach(cell => {
            keep_cells.push([Number(cell.dataset.row), Number(cell.dataset.col)])
        });

        let remove_cells = all_cells_arr.filter(element => 
            !keep_cells.some(keep => keep[0] === element[0] && keep[1] === element[1])
        );

        console.log("all cells ",all_cells_arr)
        console.log("keep cells ",keep_cells)
        console.log("remove cells ",remove_cells)


        fetch("/create_board", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ remove_list: remove_cells })  // send your array
        })
        .then(response => response.json())
        .then(data => {
            updateGameBoard(data.board);
            console.log(data.status);
        })
        .catch(error => console.error("Error:", error));
    });
});


function premade_setup(presetCells) {
    document.querySelectorAll(".sudoku-cell").forEach(cell => {
        const r = Number(cell.dataset.row);
        const c = Number(cell.dataset.col);

        if (presetCells.some(([pr, pc]) => pr === r && pc === c)) {
        cell.classList.add("selected");
        }
    });
}


function start_up() {
    fetch("/start_up")
        .then(response => response.json())
        .then(data => {
            updateGameBoard(data.board);
            console.log(data.board)
        })
        .catch(error => console.error("Error fetching board:", error));
}

// Function to update the game board dynamically
function updateGameBoard(board) {
    let boardElement = document.getElementById("game-board");
    boardElement.innerHTML = ""; // Clear existing board


    for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
            let cell = document.createElement("div");
            cell.classList.add("sudoku-cell");

            cell = create_cells(row, col, cell, board)
            
            boardElement.appendChild(cell);
        }
    }
}


function create_cells(row, col, cell, board) {
    let value = board[row][col];
    let cell_select = true;
    let keep_cells = []

    cell.dataset.row = row;
    cell.dataset.col = col;
    
    if (value !== 0) {
        cell.textContent = value; // Show pre-filled number
        cell.style.fontWeight = "bold"; // Make initial numbers stand out
    } else {
        cell.textContent = "";
    }
    
    cell.addEventListener("click", function () {
        if (cell_select == true) {
            cell.classList.toggle("selected");
            const selected_cells = document.querySelectorAll(".sudoku-cell.selected");
            document.getElementById("cells-selected").textContent = 'Cells currently selected: '+selected_cells.length

            
            
        } else {
            let number = prompt("Enter a number (1-9):");
            if (number >= 1 && number <= 9) {
                cell.textContent = number;
            }
        }
    });
    return cell
}


    
