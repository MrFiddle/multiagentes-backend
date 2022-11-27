import matplotlib.pyplot as plt
import numpy as np
import random
import json
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

if __name__ == '__main__':

    class Car:
        def __init__(self, id, initialPosition) -> None:
            self.id = id
            self.initialPosition = initialPosition

            self.coordinates = []
            self.coordinates.append(initialPosition)       
        
        def getId(self):
            return self.id
        
        def getCoordinates(self):
            return self.coordinates
        
        def getInitialPosition(self):
            print(self.coordinates)
            return initialPosition
        
        def addCoordinates(self, coordinates):
            self.coordinates.append(coordinates)
        
    
    initialPosition = [34, 10, 4]
    car = Car(1, initialPosition)
    print(car.getInitialPosition)

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