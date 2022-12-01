# Model design
import agentpy as ap
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import IPython
import random
import time

import json
from flask import Flask, request, jsonify, send_file
#import json_request

# in starting points (13,0), the car should be able to also go to the another track
# in other words to (14,0), according to this grid this is the formost left lane

# in starting points (0,13), the car should be able to algo fo to the another track
# in other words (0,12) for example, accordint to this gris this is the foremost upway lane

# in starting points (12,24), the car should be able to also go to the another track
# in other words to (11,24), according to this grid this is the foremost right lane

#in starting points (24,14), the car should be able to also go to the another track
# in other words to (24,13), according to this grid this is the formost left lane

startingCoordinates = [(13,0),(0,11),(11,24),(24,13)]

turnPointCoordinatesLeft = [(13,11),(14,11),(9,13)]
turnPointCoordinatesRight = [(11,13),(9,13),(14,11)]
turnPointCoordinatesUp = [(11,11),(11,10),(13,14)]
turnPointCoordinatesDown = [(13,13),(13,14),(11,11)]




movement1 = (0,1) # right
movement2 = (1,0) # down
movement3 = (0,-1) # left
movement4 = (-1,0) # up

stopLightPos = [(14,12),(12,10),(10,12),(12,14)]


class Car(ap.Agent):
    def setup(self):
        self.currentSelf = 0
    def save_json(self):
        self.position =  self.model.street.positions[self]
        data = self.model.data
        id = "car"+str(self.id)
        data["steps"][self.model.t]["cars"].append({"x": self.position[0],"z":self.position[1]})

    def killAgent(self):
        self.model.street.move_to(self,(-1,-1))
        self.condition = None



class stopLight(ap.Agent):
    def setup(self):
        self.state = 5  #5: green, 6:yellow, 7: red
        self.greenDuration = 0
        self.redDuration = 0
    def stateChange(self,t):
        if(t<self.greenDuration):
            self.state=5
            return self.state            
        else:
            self.state=7
            return self.state

    def forceRed(self):
        self.state=7
        return self.state
                
            
    def save_json(self):
        data = self.model.data
        id = "trafficLight"+str(self.id)
        data["steps"][self.model.t]["stop_lights"].append({"state":self.state})



class streetIntersection(ap.Model):


    def setup(self):

        #Archivo Json
        self.data ={}
        self.data["steps"]=[]

        #define car and light agents
        self.carsl = ap.AgentList(self, self.p.n_cars,Car)
        self.carsu = ap.AgentList(self, self.p.n_cars,Car)
        self.carsr = ap.AgentList(self, self.p.n_cars,Car)
        self.carsd = ap.AgentList(self, self.p.n_cars,Car)
        self.stopLights = ap.AgentList(self,4,stopLight)

        #define parameters for each class
        self.stopLights.greenDuration = self.p.greenDuration
        self.stopLights.redDuration = self.p.redDuration
        
        self.carsl.currentTrack = 1
        self.carsu.currentTrack = 3
        self.carsr.currentTrack = 2
        self.carsl.currentTrack = 4


        self.lightCycle = (self.p.greenDuration+self.p.redDuration)



        #Create street grid
        self.street = ap.Grid(self,[self.p.size]*2,track_empty=True)

        #state initial position of the cars
        
        carspos1 = [startingCoordinates[0] for i in range(len(self.carsl))]
        carspos2 = [startingCoordinates[1] for i in range(len(self.carsl))]
        carspos3 = [startingCoordinates[2] for i in range(len(self.carsl))]
        carspos4 = [startingCoordinates[3] for i in range(len(self.carsl))]

        #add each car to thei respective side and positions as well

        self.street.add_agents(self.carsl,positions=carspos1)
        self.street.add_agents(self.carsu,positions=carspos2)
        self.street.add_agents(self.carsr,positions=carspos3)
        self.street.add_agents(self.carsd,positions=carspos4)
        self.street.add_agents(self.stopLights)

        #locate stopLights
        self.street.move_to(self.stopLights[0],stopLightPos[0])
        self.street.move_to(self.stopLights[1],stopLightPos[1])
        self.street.move_to(self.stopLights[2],stopLightPos[2])
        self.street.move_to(self.stopLights[3],stopLightPos[3])





        #CONDITIONS -> 0:delimiters 1:cars 2:inactive 
        self.stopLights[2].state = 7
        self.stopLights[0].state = 7       

        self.carsl.condition = 2
        self.carsu.condition = 1
        self.carsr.condition = 3
        self.carsd.condition = 4
        
        self.stopLights.condition = self.stopLights.state

        #Cars coming from the top
        self.upLeftTurn = [random.choice([True, False]) for i in range(len(self.carsl))]
        self.upRightTurn = [random.choice([True, False]) for i in range(len(self.carsl))]

        #Cars coming from the bottom
        self.downLeftTurn = [random.choice([True, False]) for i in range(len(self.carsl))]
        self.downRightTurn = [random.choice([True, False]) for i in range(len(self.carsl))]

        #Cars coming  from the left
        self.leftUpTurn = [random.choice([True, False]) for i in range(len(self.carsl))]
        self.leftDownTurn = [random.choice([True, False]) for i in range(len(self.carsl))]

        #Cars coming from the right 
        self.rightUpTurn = [random.choice([True, False]) for i in range(len(self.carsl))]
        self.rightDownTurn = [random.choice([True, False]) for i in range(len(self.carsl))]



        self.save_json()
        # self.lightChange = (self.p.steps/3)-1


        self.horizontalCrossovers = True
        self.desynch_n = self.p.desynchs_n
        

    
    def step(self):

        doDesynch = random.choice([True,False])
        lightsCycles = self.t%self.lightCycle

        if(lightsCycles==0 and self.horizontalCrossovers==True):
            self.horizontalCrossovers=False
        elif(lightsCycles==0 and self.horizontalCrossovers==False):
            self.horizontalCrossovers=True

        #we need to select and separate cars in different conditions as they move differently

        # left cars
        moving_carsl = self.carsl.select(self.carsl)
        # up carsS
        moving_carsu = self.carsu.select(self.carsu)
        # right cars
        moving_carsr = self.carsr.select(self.carsr)
        # down cars
        moving_carsd = self.carsd.select(self.carsd)

        # 5 green | 6 yellow | 7 red

        # if(doDesynch):
        #     # self.desynch_n-=1
        #     self.stopLights.condition=self.stopLights.forceRed()
        #     randomStopLight = random.choice(self.stopLights)
        #     randomStopLight.condition=randomStopLight.stateChange(lightsCycles)
        # else:
        if(self.horizontalCrossovers):
            self.stopLights[1].condition=self.stopLights[1].stateChange(lightsCycles)
            self.stopLights[3].condition=self.stopLights[3].stateChange(lightsCycles)

        else:
            self.stopLights[2].condition=self.stopLights[2].stateChange(lightsCycles)
            self.stopLights[0].condition=self.stopLights[0].stateChange(lightsCycles) 

        # self.stopLights[1].condition = 7 # left light
        # self.stopLights[3].condition = 7 # right light

        # self.stopLights[2].condition = 7 # up light
        # self.stopLights[0].condition = 7 # down light

        # LEFT CARS
        for i, car in enumerate(moving_carsl):

            m = movement1

            currentPos = self.street.positions[car] # get current position

            frontPos = (currentPos[0], currentPos[1] + 1) # position of the possible car in front
            frontPos2 = (currentPos[0], currentPos[1] + 2) # position of the possible car in front

            if frontPos[1] > 23 or frontPos2[1] > 24:
                continue
            
            if self.street.positions[car] == (13,8) and (7 in self.street.agents[12, 10].condition):
                continue


            if (self.leftDownTurn[i] == True) and (currentPos[1] == 11):
                frontPos = (currentPos[0] + 1, currentPos[1]) # position of the possible car in front
                frontPos2 = (currentPos[0] + 2, currentPos[1]) # position of the possible car in front
                m = movement2
                self.street.move_by(car, m)

            elif(self.leftUpTurn[i]==True) and (currentPos[1]==13):
                m = movement4
                self.street.move_by(car, m)
            
            else:
                if (len(self.street.agents[frontPos].condition) == 0 and len(self.street.agents[frontPos2].condition) == 0):
                    self.street.move_by(car, m) # move the car

            if (currentPos[1]>=22) or (currentPos[0] >= 23) or (currentPos[0]<=0):
                car.killAgent()
        
       
        # UP CARS
        for i,car2 in enumerate(moving_carsu):
            m = movement2

            currentPos = self.street.positions[car2] # get current position

            frontPos = (currentPos[0] + 1, currentPos[1]) # position of the possible car in front
            frontPos2 = (currentPos[0] + 2, currentPos[1]) # position of the possible car in front

            if frontPos[0] > 24 or frontPos2[0] > 24:
                continue

            if self.street.positions[car2] == (8, 11) and (7 in self.street.agents[10, 12].condition):
                continue


            if (self.upLeftTurn[i] == True) and (currentPos[0] == 11):
                frontPos = (currentPos[0] - 1, currentPos[1]) # position of the possible car in front
                frontPos2 = (currentPos[0] - 2, currentPos[1]) # position of the possible car in front
                m = movement3
                self.street.move_by(car2, m) # move the car

            elif(self.upRightTurn[i]==True) and (currentPos[0]==13):
                m = movement1
                self.street.move_by(car2, m) # move the car
            else:
                if (len(self.street.agents[frontPos].condition) == 0 and len(self.street.agents[frontPos2].condition) == 0):
                    self.street.move_by(car2, m)


            if (currentPos[0] >= 22) or (currentPos[1] <= 0) or (currentPos[1] >=23):
                car2.killAgent()
            

        # right cars
        for i,car3 in enumerate(moving_carsr):

            currentPos = self.street.positions[car3] # get current position

            frontPos = (currentPos[0], currentPos[1] - 1) # position of the possible car in front
            frontPos2 = (currentPos[0], currentPos[1] - 2) # position of the possible car in front

            if frontPos[0] < 1 or frontPos2[0] < 1:
                continue

            if currentPos == (11, 16)  and (7 in self.street.agents[12, 14].condition):
                continue

            if (self.rightUpTurn[i] == True) and (currentPos[1] == 13):
                frontPos = (currentPos[0] - 1, currentPos[1]) # position of the possible car in front
                frontPos2 = (currentPos[0] - 2, currentPos[1]) # position of the possible car in front
                m = movement4
                self.street.move_by(car3, m) # move the car

            elif(self.rightDownTurn[i]==True) and (currentPos[1]==11):
                m=movement2
                self.street.move_by(car3, m) # move the car

            else:
                if (len(self.street.agents[frontPos].condition) == 0 and len(self.street.agents[frontPos2].condition) == 0):
                    self.street.move_by(car3, movement3)


            
            if (currentPos[1] <= 2) or (currentPos[0]<=1) or (currentPos[0]>=23):                
                car3.killAgent()
 
        
        # down cars
        for i,car4 in enumerate(moving_carsd):

            currentPos = self.street.positions[car4]

            frontPos = (currentPos[0] - 1, currentPos[1])
            frontPos2 = (currentPos[0] - 2, currentPos[1])

            if frontPos[0] < 0 or frontPos2[0] < 0:
                continue
            if self.street.positions[car4] == (16, 13) and (7 in self.street.agents[14, 12].condition):
                continue

            if (self.downRightTurn[i] == True) and (currentPos[0] == 13):
                frontPos = (currentPos[0] - 1, currentPos[1]) # position of the possible car in front
                frontPos2 = (currentPos[0] - 2, currentPos[1]) # position of the possible car in front
                m = movement1
                self.street.move_by(car4, m) # move the car

            elif(self.downLeftTurn==True) and (currentPos[0]==11):
                m=movement3
                self.street.move_by(car4, m) # move the car

            else:
                if (len(self.street.agents[frontPos].condition) == 0 and len(self.street.agents[frontPos2].condition) == 0):
                    self.street.move_by(car4, movement4)


            if (currentPos[0] <= 2) or (currentPos[1]>=24) or (currentPos[1]<=0):
                car4.killAgent()

        self.save_json()
        
        
    def save_json(self):
        self.data["steps"].append({})
        self.data["steps"][self.model.t]["cars"] = []
        
        self.carsl.save_json()
        self.carsr.save_json()
        self.carsu.save_json()
        self.carsd.save_json()


        self.data["steps"][self.model.t]["stop_lights"] = []

        self.stopLights.save_json()

    def end(self):
        print("jsonmaking")
        json_file = json.dumps(self.data,indent=2)
        with open('data.json','w') as outfile:
            outfile.write(json_file)