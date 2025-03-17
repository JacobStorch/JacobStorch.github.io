document.addEventListener("DOMContentLoaded", function() {
    fetch("/get-board")
        .then(response => response.json())
        .then(sudokuBoard => {
            let board = document.getElementById("game-board");

            for (let row = 0; row < 9; row++) {
                for (let col = 0; col < 9; col++) {
                    let cell = document.createElement("div");
                    cell.classList.add("sudoku-cell");
                    cell.dataset.index = row * 9 + col;

                    if (sudokuBoard[row][col] !== null) {
                        cell.textContent = sudokuBoard[row][col];
                        cell.style.fontWeight = "bold"; // Make initial numbers stand out
                    } else {
                        cell.addEventListener("click", function() {
                            let number = prompt("Enter a number (1-9):");
                            if (number >= 1 && number <= 9) {
                                cell.textContent = number;
                            }
                        });
                    }
                    board.appendChild(cell);
                }
            }
        });
});

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("remove-cells").addEventListener("click", function () {
        let rCount = document.getElementById("cells-to-remove").value;

        fetch("/remove_cells", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ r_count: rCount }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        })
        .catch(error => console.error("Error:", error));
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("new-game").addEventListener("click", function () {
        fetch("/new_game", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                updateGameBoard(data.board);  // Function to update the board
            }
        })
        .catch(error => console.error("Error:", error));
    });
});

function updateGameBoard(board) {
    let boardElement = document.getElementById("game-board");
    boardElement.innerHTML = "";  // Clear existing board

    for (let i = 0; i < 81; i++) {
        let cell = document.createElement("div");
        cell.classList.add("sudoku-cell");
        cell.dataset.index = i;
        cell.textContent = board[Math.floor(i / 9)][i % 9] || ""; // Fill cell with value
        cell.addEventListener("click", function () {
            let number = prompt("Enter a number (1-9):");
            if (number >= 1 && number <= 9) {
                cell.textContent = number;
            }
        });
        boardElement.appendChild(cell);
    }
}

console.log("Script loaded!"); 
