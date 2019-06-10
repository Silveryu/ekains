from constants import *
import logging

class Snake:
    def __init__(self, body, direction, name, gameid=None):
        self.body=body #initially located here
        self.name=name
        self.direction=self.newdirection=direction
        self.IsDead=False
        self.points = 0
        logging.basicConfig(format=':%(levelname)s:%(message)s', level=logging.DEBUG)
    def ping(self):
        #only used by netagent to measure latency between players
        return 0
    def destroy(self):
        pass
    def updateBody(self, body):
        self.body = body
        return 0 #time took to update
    def update(self,points=None, mapsize=None, count=None, agent_time=None):
        #send players stats about the game 
        return 0 #time took to update
    def updateDirection(self,game):
        self.direction=self.newdirection #the next direction is stored in newdirection....logic is updated here
        return 0 #time took to update
    def processkey(self,key):
        pass #nothing to do here it is just to support human players

