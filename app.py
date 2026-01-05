from flask import Flask, request, jsonify, render_template
import sudoku  # Assuming you have sudoku.py with game logic

app = Flask(__name__)

@app.route('/new_game', methods=['POST'])
def new_game():
    board = sudoku.s_gen()  # Call the function that generates a new board
    return jsonify({'status': 'success', 'board': board})  # Send back the new board

@app.route("/get_board")
def get_board():
    board = sudoku.get_current_board()
    return jsonify({"board": board})

@app.route("/create_board", methods=["POST"])
def create_board():
    data = request.get_json()
    print('data error',data)
    remove_list = data['remove_list']
    sudoku.s_gen()
    sudoku.remove_init(remove_list,False)
    board = sudoku.get_current_board()
    return jsonify({"board": board})

@app.route("/start_up", methods=["GET"])
def start_up():
    sudoku.create_empty_board()
    board = sudoku.get_current_board()
    return jsonify({"board": board})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
