document.addEventListener("DOMContentLoaded", function () {
    // Fetch and display the initial board
    loadBoard();

    // Event listener for New Game button
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
                updateGameBoard(data.board);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    document.querySelectorAll('.sudoku-cell').forEach(cell => {
      cell.addEventListener('click', () => {
        cell.classList.toggle('selected');
      });
    });

    // Event listener for Remove Cells button
    document.getElementById("remove-cells").addEventListener("click", function () {
        let rCount = document.getElementById("cells-selected").value;

        fetch("/remove_cells", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ r_count: rCount }),
        })
        .then(response => response.json())
        .then(board => {
            updateGameBoard(data.board);
            console.log(data.status);
        })
    });
});

// Function to fetch and display the Sudoku board
function loadBoard() {
    fetch("/get_board")
        .then(response => response.json())
        .then(data => {
            updateGameBoard(data.board);
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

            let value = board[row][col];
            if (value !== 0) {
                cell.textContent = value; // Show pre-filled number
                cell.style.fontWeight = "bold"; // Make initial numbers stand out
            } else {
                cell.textContent = "";
                cell.addEventListener("click", function () {
                    let number = prompt("Enter a number (1-9):");
                    if (number >= 1 && number <= 9) {
                        cell.textContent = number;
                    }
                });
            }

            boardElement.appendChild(cell);
        }
    }
}
