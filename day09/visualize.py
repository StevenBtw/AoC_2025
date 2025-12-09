import json
import os
import queue
import threading
from solution import parse_input, maximize_rectangle
from flask import Flask, Response, request, send_file
from ortools.sat.python import cp_model

os.chdir(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__)
tiles = parse_input("input.txt")


class WebCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, q, tiles, selected, x1, x2, y1, y2):
        super().__init__()
        self.q, self.tiles, self.selected = q, tiles, selected
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2
        self.count = 0

    def on_solution_callback(self):
        self.count += 1
        self.q.put({
            'solution_num': self.count,
            'area': int(self.ObjectiveValue()),
            'selected_tiles': [i for i in range(len(self.tiles)) if self.Value(self.selected[i])],
            'rect': {'x1': self.Value(self.x1), 'x2': self.Value(self.x2),
                     'y1': self.Value(self.y1), 'y2': self.Value(self.y2)}
        })


@app.route('/')
def index():
    return send_file('solution.html')


@app.route('/tiles_data')
def tiles_data():
    return json.dumps({'tiles': tiles})


@app.route('/solve')
def solve():
    part = int(request.args.get('part', 1))

    def generate():
        q = queue.Queue()

        def run():
            result = maximize_rectangle(tiles, part=part, callback_factory=lambda sel, x1, x2, y1, y2: WebCallback(q, tiles, sel, x1, x2, y1, y2))
            q.put({'done': True, 'status': result['status'] if result else 'NO_SOLUTION'})

        threading.Thread(target=run).start()
        while True:
            try:
                data = q.get(timeout=30)
                yield f"data: {json.dumps(data)}\n\n"
                if data.get('done'):
                    break
            except queue.Empty:
                break

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    print("Starting server at http://localhost:5000")
    app.run()
