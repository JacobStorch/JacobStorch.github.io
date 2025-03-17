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
            alert(data.message);  // Show confirmation
        })
        .catch(error => console.error("Error:", error));
    });
});

console.log("Script loaded!"); 
