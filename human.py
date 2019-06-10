from snake import Snake
from pygame.locals import *
from constants import *

class Human(Snake):  ### class name now matches module name!
    def __init__(self,body=[(0,0)] , direction=(1,0), name="Human"):
        super().__init__(body,direction,name=name)
        #assign the keys to control the human snake
        self.upkey=K_UP
        self.downkey=K_DOWN
        self.rightkey=K_RIGHT
        self.leftkey=K_LEFT
        
    def processkey(self,key):
        #we check the old direction not the new direction.
        if key==self.upkey:
            if self.direction != down:
                self.newdirection=up
        elif key==self.downkey:
            if self.direction != up:
                self.newdirection=down
        elif key==self.rightkey:
            if self.direction != left:
                self.newdirection=right
        elif key==self.leftkey:
            if self.direction != right:
                self.newdirection=left

### An alias for the class name, to keep backward compatibility.
HumanSnake = Human

