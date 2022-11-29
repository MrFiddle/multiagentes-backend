import json
from flask import Flask, request, jsonify, send_file
import backend
from backend import streetIntersection

app = Flask(__name__)

@app.route('/cars', methods=['GET'])
def helloWorld():
    parameters = {
        'size': 25,
        'steps': 200,
        'n_cars': request.args.get('n_cars', default=4, type=int),
        'greenDuration': 10,
        'redDuration': 15
    }

    street = streetIntersection(parameters)
    street.run()

    with open ('data.json') as f:
        data = json.load(f)
        return data

def main():
    app.run()