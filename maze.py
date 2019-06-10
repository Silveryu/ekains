import copy
import json

class Maze:
    def __init__(self, o, p, f):
        self.obstacles = copy.deepcopy(o)
        self.playerpos = copy.deepcopy(p)
        self.foodpos = copy.deepcopy(f)
    def toNetwork(self):
        p = json.dumps({'obstacles': self.obstacles, 'playerpos': self.playerpos, 'foodpos': self.foodpos})
        return p 
    def fromNetwork(self, p):
        s = json.loads(p)
        #JSON can't encode tuples, it encodes it as lists... lets fix it:
        self.obstacles = [(e[0], e[1]) for e in s['obstacles']]
        self.playerpos = [(e[0], e[1]) for e in s['playerpos']]
        self.foodpos = s['foodpos'][0], s['foodpos'][1]
    def __str__(self):
        return "obstacles = {}  playerpos = {}  foodpos = {}".format(str(self.obstacles), str(self.playerpos), str(self.foodpos))
