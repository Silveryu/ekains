from enum import Enum

#Colours
Black = (0,0,0)
White = (255,255,255)
Red = (255,0,0)
Lime = (0,255,0)
Blue = (0,0,255)
Yellow = (255,255,0)
Cyan = (0,255,255)
Magenta = (255,0,255)
Silver = (192,192,192)
Gray = (128,128,128)
Maroon = (128,0,0)
Olive = (128,128,0)
Green = (0,128,0)
Purple = (128,0,128)
Teal = (0,128,128)
Navy = (0,0,128)
colours = [Red, Lime, Blue, Yellow, Cyan, Magenta, Silver, Gray, Maroon, Olive, Green, Purple, Teal, Navy]


#direction of snake
left=-1,0
right=1,0
up=0,-1
down=0,1
directions=[up,down,right,left]

#update returns
class AgentUpdate(Enum):
    nothing=0
    died=1
    ate_food=2

