from flask import Flask, request, jsonify, render_template
import sudoku, os  # Import your existing sudoku.py file

app = Flask(__name__)

@app.route('/remove_cells', methods=['POST'])
def remove_cells():
    data = request.get_json()
    r_count = int(data['r_count'])
    
    sudoku.remove_init(r_count)  # Ensure this function exists and works correctly

    return jsonify({'status': 'success', 'message': f'Removed {r_count} cells'})

@app.route("/")
def index():
    return render_template("index.html")  # Make sure index.html is inside templates/

@app.route("/get-board")
def get_board():
    if hasattr(sudoku, "board"):  # Check if sudoku.py has a 'board' variable
        return jsonify(sudoku.board)
    return jsonify({"error": "Board not found"}), 500

@app.route("/new_game", methods=["POST"])
def new_game():
    board = sudoku.s_gen()  # Call s_gen() to generate a new Sudoku board
    return jsonify({"status": "success", "board": board})  # Send board data

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if PORT is missing
    app.run(host="0.0.0.0", port=port, debug=True)
