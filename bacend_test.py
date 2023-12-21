from flask import Flask, request, jsonify
import numpy as np
import time
import json

app = Flask(__name__)

@app.route('/add', methods=['POST'])
def add():
    start_time = time.time()

    data = request.get_json(force=True)
    a = np.array(data['a'])
    b = np.array(data['b'])
    time_java = np.array(data['java_start_time'])
    c = a * b

    end_time = time.time()
    start_time_ms = start_time
    time_java_ms = time_java /1000
    difference = start_time_ms - time_java_ms
    print(start_time_ms)
    print(time_java_ms)
    print(difference)
    result = {
        "result": c.tolist(),
        "start_time": start_time,
        "end_time": end_time
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)