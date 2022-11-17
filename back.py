import matplotlib.pyplot as plt
import numpy as np
import random
import json
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

if __name__ == '__main__':


    class Car:
        def __init__(self, id, x, y, z) -> None:
            self.id = id
            self.x = x
            self.y = y
            self.z = z
        
        def getX(self):
            return self.x
        
        def getY(self):
            return self.y

        def getZ(self):
            return self.z
        
        def getId(self):
            return self.id

    @app.route('/cars', methods=['GET'])
    def getCars():

        cars = []
        carNumber = 20
        counter = 1

        for i in range(carNumber):

            x = random.uniform(0, 100)
            z = random.uniform(0, 100)
            cars.append(Car("car" + str(counter),x, 0, z))
            counter = counter + 1

            print(counter)

        def createJson():
            with open('cars.json', 'w') as f:
                json.dump(cars, f, default=lambda o: o.__dict__, indent=4)
        
        createJson()
        return send_file('cars.json')
    
    app.run(debug=True, port=8000)