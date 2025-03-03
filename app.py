from flask import Flask, request, jsonify, render_template
import sudoku  # This imports your existing sudoku.py file
from sudoku import board

app = Flask(__name__)

@app.route('/remove_cells', methods=['POST'])
def remove_cells():
    data = request.get_json()  # Get the JSON data sent from the frontend
    r_count = int(data['r_count'])  # Extract the r_count value

    # Call the remove_init function from sudoku.py and pass r_count
    sudoku.remove_init(r_count)  # Modify the remove_init function to accept r_count

    return jsonify({'status': 'success', 'message': f'Removed {r_count} cells'})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get-board")
def get_board():
    return jsonify(board)

if __name__ == "__main__":
    app.run(debug=True)

