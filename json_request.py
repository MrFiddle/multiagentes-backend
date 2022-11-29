import json
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

@app.route('/cars', methods=['GET'])
def helloWorld():

    with open ('data.json') as f:
        data = json.load(f)
        return data

def main():
    app.run()