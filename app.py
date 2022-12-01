import json
from flask import Flask, request, jsonify, send_file
from backend import streetIntersection

app = Flask(__name__)

@app.route('/cars', methods=['GET'])
def helloWorld():
    parameters = {
        'size': 25,
        'steps': 200,
        'n_cars': request.args.get('n_cars', default=4, type=int),
        'greenDuration': 10,
        'redDuration': 15,
        'desynchs_n':4
    }

    street = streetIntersection(parameters)
    street.run()

    with open ('data.json') as f:
        data = json.load(f)
        return data

def main():
    app.run()