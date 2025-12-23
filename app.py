from flask import Flask, request, jsonify, render_template
import sudoku  # Assuming you have sudoku.py with game logic

app = Flask(__name__)

@app.route('/new_game', methods=['POST'])
def new_game():
    board = sudoku.s_gen()  # Call the function that generates a new board
    return jsonify({'status': 'success', 'board': board})  # Send back the new board

@app.route('/remove_cells', methods=['POST'])
def remove_cells():
    data = request.get_json()
    r_count = int(data['r_count'])
    # Call remove_init to remove the cells
    board = sudoku.remove_init(r_count)
    return jsonify({'status': 'success', 'board': board})

@app.route("/get_board")
def get_board():
    board = sudoku.get_current_board()
    return jsonify({"board": board})

@app.route("/create_board")
def create_board():
    sudoku.s_gen()
    board = sudoku.get_current_board()
    return jsonify({"board": board})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
