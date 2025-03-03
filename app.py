from flask import Flask, request, jsonify, render_template
import sudoku  # Import your existing sudoku.py file

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

if __name__ == "__main__":
    app.run(debug=True)
