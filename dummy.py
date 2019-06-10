from snake import Snake
from constants import *

class Dummy(Snake):
    def __init__(self,body=[(0,0)] , direction=(1,0), name="Dummy"):
        super().__init__(body,direction,name=name)
    def update(self,points=None, mapsize=None, count=None,agent_time=None):
        pass
    def updateDirection(self,maze):
        if self.direction == (1,0):
            self.direction=(-1,0)
        else:
            self.direction=(1,0)
 
