import random
import json

class Car:
    def __init__(self, x, y, z) -> None:
        self.x = x
        self.y = y
        self.z = z
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y

    def getZ(self):
        return self.z

    
cars = []
carNumber = 20

for i in range(carNumber):
    x = random.uniform(0, 100)
    # y = random.uniform(0, 100)
    z = random.uniform(0, 100)
    cars.append(Car(x, 0, z))

for i in cars:
    print("x: " + str(i.getX()), "y: " + str(i.getY()), "z: " + str(i.getZ()))

with open('cars.json', 'w') as f:
    json.dump(cars, f, default=lambda o: o.__dict__, indent=4)