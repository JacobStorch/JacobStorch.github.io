let play_mode = false;
let current_board = null;
let full_board = null;
let note_mode = false;


document.addEventListener("DOMContentLoaded", function () {
    start_up();
    play_mode = false

    document.getElementById("new-game").addEventListener("click", function (e) {
        e.preventDefault();

        play_mode = false

        fetch("/start_up")
            .then(response => {
                console.log("RAW RESPONSE:", response);
                return response.text();
            })
            .then(text => {
                console.log("RAW TEXT:", text);
                const data = JSON.parse(text);
                console.log("PARSED DATA:", data);
                document.getElementById("create-board").disabled = false;
                updateGameBoard(data.board);
            })
            .catch(error => console.error("FETCH ERROR:", error));
    });

    document.getElementById("premade-house").addEventListener("click", function () {
        const preset_cells = [[0,0],[0,1],[0, 4],[0,8],[1,3],[1,4],[1, 5],[1,8],[2,2],[2,3],[2,5],[2,6],[3,1],[3,2],[3,6],[3,7],[4,0],[4,1],[4, 3],[4,5],[4,7],[4,8],[5,1],[5,3],[5,5],[5,7],[6,1],[6,7],[7, 1],[7,3],[7,5],[7,7],[8, 1],[8,3],[8,7]];
    
    premade_setup(preset_cells)
    })

    document.getElementById("premade-stripes").addEventListener("click", function () {
        const preset_cells = [[0,0],[0,3],[0,6],[1,1],[1,4],[1,7],[2,2],[2,5],[2,8],[3,0],[3,3],[3,6],[4,1],[4,4],[4,7],[5,2],[5,5],[5,8],[6,0],[6,3],[6,6],[7,1],[7,4],[7,7],[8,2],[8,5],[8,8]];

        premade_setup(preset_cells)
    })

    document.getElementById("candidate-switch").addEventListener("click", function () {
        console.log("Switch")
        const candidates = document.querySelector(".candidates");
        const candidate_switch = document.getElementById("candidate-switch");
        note_mode = candidate_switch.checked
        if (note_mode) {
            document.querySelectorAll(".candidates").forEach(candidates => {
                candidates.style.display = "grid";
            });
        } else {
            document.querySelectorAll(".candidates").forEach(candidates => {
                candidates.style.display = "none";
            });
}
    })

    document.getElementById("create-board").addEventListener("click", function () {
        showLoading();
        
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
            play_mode = true
            updateGameBoard(data.board);
            hideLoading();
            document.getElementById("create-board").disabled = true;
        })
        .catch(error => console.error("Error:", error));


        fetch("/get_full_board")
        .then(response => response.json())
        .then(data => {
            full_board = data.board;
            console.log(full_board);
        })
        .catch(error => console.error("Error fetching full board:", error));
    });
});


function premade_setup(presetCells) {
    document.querySelectorAll(".sudoku-cell").forEach(cell => {
         cell.classList.remove("selected");

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
            current_board = data.board;
            updateGameBoard(current_board);
            console.log(current_board);
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

    let cellData = board[row][col];

    if (cellData === null || typeof cellData !== "object") {
        if (full_board !== null) {
            correct_val= full_board[row][col]
        } else {
            correct_val = null
        }

        cellData = {
            given: cellData,   // number OR null
            user: null,
            correct: correct_val
        };

        board[row][col] = cellData;
    }

    const { given, user, correct } = cellData;

    cell.dataset.row = row;
    cell.dataset.col = col;
    cell.innerHTML = "";
    cell.classList.remove("has-value");
    delete cell.dataset.locked;

    if (given !== null) {
        const numberDiv = document.createElement("div");
        numberDiv.classList.add("cell-value", "given-value");
        numberDiv.textContent = given;

        cell.appendChild(numberDiv);
        cell.classList.add("has-value");
        cell.dataset.locked = "true";   // 🔒 mark as locked
        return cell;
    }

    if (user !== null) {
        const numberDiv = document.createElement("div");
        numberDiv.classList.add("cell-value", "user-value");
        numberDiv.textContent = user;

        cell.appendChild(numberDiv);
        cell.classList.add("has-value");
    } 
    else if (play_mode === true) {
        cell.appendChild(createCandidates());
    }

    cell.addEventListener("click", function (e) {
        if (cell.dataset.locked === "true") return;

        // Clear other selections
        document.querySelectorAll(".sudoku-cell").forEach(c => c.classList.remove("selected"));

        if (note_mode) {
            // Show / toggle candidate grid instead of selecting the cell
            const candidates = cell.querySelector(".candidates");
            if (candidates) {
                // toggle visibility
                candidates.style.display = candidates.style.display === "grid" ? "none" : "grid";
                if (e.target.tagName === "SPAN") {
                    console.log(`Candidate clicked: ${e.target.textContent} at ${row},${col}`);
                }
            }
        } else {
            // Normal mode: select the cell
            cell.classList.add("selected");

            // hide candidates if they exist
            const candidates = cell.querySelector(".candidates");
            if (candidates) candidates.style.display = "none";
        }
    });

    return cell;
}

function update_cells(row,col,cell,board) {
    let cellData = board[row][col];
    const { given, user, correct } = cellData;

    cell.dataset.row = row;
    cell.dataset.col = col;
    cell.innerHTML = "";
    cell.classList.remove("has-value");
    delete cell.dataset.locked;

    if (given !== null) {
        const numberDiv = document.createElement("div");
        numberDiv.classList.add("cell-value", "given-value");
        numberDiv.textContent = given;

        cell.appendChild(numberDiv);
        cell.classList.add("has-value");
        cell.dataset.locked = "true";   // 🔒 mark as locked
        console.log("cd E",cellData);
        return cell;
    }

    if (user !== null) {
        const numberDiv = document.createElement("div");
        numberDiv.classList.add("cell-value", "user-value");
        numberDiv.textContent = user;

        cell.appendChild(numberDiv);
        cell.classList.add("has-value");
    } 
    else if (play_mode === true) {
        cell.appendChild(createCandidates());
    }
}

document.addEventListener("keydown", function (e) {
    if (!play_mode) return;

    const selectedCell = document.querySelector(".sudoku-cell.selected");
    if (!selectedCell) return;
    if (selectedCell.dataset.locked === "true") return;

    const row = +selectedCell.dataset.row;
    const col = +selectedCell.dataset.col;

    if (e.key === "Backspace" || e.key === "Delete") {
        current_board[row][col].user = null;
        update_cells(row,col,selectedCell,current_board);
        return;
    }

    if (/^[1-9]$/.test(e.key)) {
        current_board[row][col].user = Number(e.key);
        update_cells(row,col,selectedCell,current_board);
    }
});

function showLoading() {
    document.getElementById("loading").style.display = "block";
}

function hideLoading() {
    document.getElementById("loading").style.display = "none";
}

function createCandidates() {
    const container = document.createElement("div");
    container.classList.add("candidates");
    container.style.display = "none"; // initially hidden

    for (let i = 1; i <= 9; i++) {
        const span = document.createElement("span");
        span.textContent = i;
        container.appendChild(span);
    }

    container.addEventListener("click", function(e) {
        if (e.target.tagName === "SPAN") {
            const selectedCell = container.parentElement;
            const row = +selectedCell.dataset.row;
            const col = +selectedCell.dataset.col;

            // write the pencil note (you can store it in cellData.user or a separate notes array)
            console.log(`Candidate clicked: ${e.target.textContent} at ${row},${col}`);
        }
    });

    return container;
}

