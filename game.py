# Snake Game Version 1.0 
# Initially based on the code provided by http://www.virtualanup.com at https://gist.githubusercontent.com/virtualanup/7254581/raw/d69804ce5b41f73aa847f4426098dca70b5a1294/snake2.py
# Diogo Gomes <dgomes@av.it.pt>
import uuid
import copy
import sys
from collections import namedtuple
from sys import exit
import pygame,random
from pygame.locals import *
from constants import *
from maze import Maze
from netagent import NetAgent

import logging

class Player:
    def __init__(self, agent, color=(255,0,0)):
        self.agent = agent 
        self.body = agent.body 
        self.name = agent.name
        self.color = color
        r,g,b = color
        f = 0.50
        self.head_color = (int(r+(255-r)*f), int(g+(255-g)*f), int(b+(255-b)*f))
        self.IsDead = False
        self.points = 0
        self.latency = 0 
    def kill(self):
        if not self.IsDead:
            self.IsDead = True
            self.agent.IsDead = True
            self.point(-1000)
            logging.info("Player <{}> died".format(self.name))
    def point(self, point):
        self.points+=point
        self.agent.points+=point
        logging.info("Player <{}> points: {}".format(self.name, self.points))

class SnakeGame:
    def __init__(self, hor=60, ver=40, tilesize=20, fps=50, visual=False, obstacles=15, mapa=None, timeout=sys.maxsize):
        self.tilesize=tilesize  #tile size, adjust according to screen size
        self.hortiles=hor   #number of horizontal tiles
        self.verttiles=ver  #number of vertical tiles
        self.timeout=timeout #maximum number of cycles 
        self.gameid=uuid.uuid4() 
        logging.basicConfig(format='%(levelname)s<{}>\t%(message)s'.format(self.gameid), level=logging.DEBUG) 

        if mapa != None:
            image = pygame.image.load(mapa)
            pxarray = pygame.PixelArray(image)
            self.hortiles=len(pxarray)
            self.verttiles=len(pxarray[0])

        if visual: 
            #create the window and do other stuff
            pygame.init()
            self.screen = pygame.display.set_mode(((self.hortiles)*self.tilesize,(self.verttiles)*self.tilesize+25), pygame.RESIZABLE)
            pygame.display.set_caption('Python Snake')
        
            #load the font
            self.font = pygame.font.Font(None, 30)
            self.obscolor=(139,69,19)
            self.foodcolor=(0,255,0)
        else:
            self.screen = None
        
        self.playerpos=[]
        self.obstacles=[]
        self.foodfield=[]
        self.playerfield=[]
        self.fps=fps #frames per second. The higher, the harder
        if not self.loadMap(mapa):
            self.setObstacles(obstacles)
        self.generateFood()

    def generateFood(self):
        if len(self.foodfield) > 0:
            self.foodpos=random.choice(self.foodfield)
            while(self.foodpos in self.playerpos):
                self.foodpos=random.choice(self.foodfield)
            return

        self.foodpos=random.randrange(0,self.hortiles),random.randrange(0,self.verttiles)
        while (self.foodpos in self.playerpos or self.foodpos in self.obstacles):
            self.foodpos=random.randrange(0,self.hortiles),random.randrange(0,self.verttiles)

    def playerPos(self):
        if len(self.playerfield) > 0:
            pos = random.choice([p for p in self.playerfield if not p in self.playerpos])
            self.playerpos.append(pos)
            return pos

        pos = random.randrange(1, self.hortiles), random.randrange(1, self.verttiles)
        while (pos in self.obstacles):
            pos = random.randrange(1, self.hortiles), random.randrange(1, self.verttiles)
        return pos
   
    def loadMap(self, filename=None):
        if filename != None:
            logging.info("Loading {} ...".format(filename))
            image = pygame.image.load(filename)
            pxarray = pygame.PixelArray(image)
            for x in range(len(pxarray)):
                for y in range(len(pxarray[x])):
                    p = pxarray[x][y] & 0xFFFFFFFF #fix signed/unsigned
                    if p == 0xFF000000:
                        p = 0xAA7942
                    if p == 0:
                        p = 0xFFFFFF
                    p = p & 0xFFFFFF
                    if not p in [0x00F900, 0xFF2600, 0xAA7942, 0x000000, 0xFFFFFF, 0]: #food, player, wall, oldwall, empty, oldempty 
                        logging.error("UNKNOWN: {:02X}".format(p))
                    if p == 0x00F900:
                        self.foodfield.append((x,y))
                    elif p == 0xFF2600:
                        self.playerfield.append((x,y))
                    elif p == 0xAA7942: 
                        self.obstacles.append((x, y))
            return True
        return False

    def setObstacles(self,level):
        for i in range(1,level+1):
            lo=random.randrange(0,self.hortiles),random.randrange(0,self.verttiles) #last obstacle
            self.obstacles.append(lo)
            for j in range(1,random.randint(1,level)):
                if random.randint(1,2) == 1:
                    lo=(lo[0]+1,lo[1])
                else:
                    lo=(lo[0],lo[1]+1)
                if 0<=lo[0]<self.hortiles and 0<=lo[1]<self.verttiles :
                    self.obstacles.append(lo)

    def setPlayers(self,players):
        self.players=[]
        if self.screen != None:
            colors = [c for c in colours if c not in [self.obscolor, self.foodcolor]]
        else:
            colors = colours

        for p in players:
            c = random.choice(colors)
            colors.remove(c)
            self.players+=[Player(p,c)]
        self.dead=[]

    def printstatus(self):
        PlayerStat = namedtuple('PlayerStat', 'name color points')
        players = [PlayerStat(p.name, p.color, p.points) for p in self.players + self.dead]
      
        score = "{} vs {}".format(players[0].points, players[1].points)
        if self.screen == None and (self.count % self.fps == 0 or self.count >= self.timeout):
            logging.info("{} {} {}".format(players[0].name, score, players[1].name))
        elif self.screen != None:
            text = self.font.render(score, 1,(255,255,255))
            textpos = text.get_rect(centerx=self.screen.get_width()/2,y=(self.verttiles)*self.tilesize)

            player1_name=self.font.render(players[0].name,1,players[0].color)
            player1_pos = player1_name.get_rect(x=self.screen.get_width()/2 - self.font.size(score + players[0].name)[0],y=(self.verttiles)*self.tilesize)

            player2_name=self.font.render(players[1].name,1,players[1].color)
            player2_pos = player2_name.get_rect(x=self.screen.get_width()/2 + self.font.size(score)[0],y=(self.verttiles)*self.tilesize)
            
        
            self.screen.blit(player1_name, player1_pos)
            self.screen.blit(player2_name, player2_pos)
            self.screen.blit(text, textpos)
      
        text=None
        if len([p for p in self.players if not p.IsDead]) == 1:
            w = [p for p in self.players if not p.IsDead][0]
            winner = "{} is the Winner!".format(w.name)
            if self.screen == None:
                logging.info(winner)
            else:
                text=self.font.render(winner,1,w.color)
        elif len([p for p in self.players if not p.IsDead]) == 0:
            dead = "All dead..."
            if self.screen == None:
                logging.info(dead)
            else:
                text=self.font.render(dead,1,(255,0,0))
        if text != None and self.screen != None:
            textpos = text.get_rect(centerx=self.screen.get_width()/2,centery=self.screen.get_height()/2)
            self.screen.blit(text, textpos)
    
    def updatePlayerInfo(self):
        #update where the players are in the board just before updating the logic
        self.playerpos=[]
        for player in self.players:
            if not player.agent.IsDead:
                self.playerpos+=player.body
            try:
                b = lambda x: x.agent.update(points=[(a.name, a.points) for a in self.players], mapsize=(self.hortiles, self.verttiles), count=self.count, agent_time=1000*(1/self.fps)/2) #update game logic (only for alive players)
                self.timekeep(player, b)
            except Exception as error:
                logging.error(str(error))
                player.kill()

    def gameKill(self, snake):
       snake.kill()
       self.updatePlayerInfo()
       self.dead.append(snake)

    def timekeep(self, player, block):
        s = pygame.time.get_ticks()
        timespent = block(player) 
        f = pygame.time.get_ticks() 
        if timespent == None:
            timespent = f-s 

        if timespent > 1000*(1/self.fps)/2:
            logging.debug("({})\ttimedif={}\t\ttimespent={}".format(player.name, f-s,timespent))
            logging.info("Player <{}> took {}".format(player.name, timespent))
            player.point(-10)   #we penalize players that take longer then a half a tick

    def update(self,snake):
        #updates the snake...
        r = AgentUpdate.nothing

        head=snake.body[0]#head of snake
        if (abs(snake.agent.direction[0]) + abs(snake.agent.direction[1])) > 1:
            self.gameKill(snake)
            logging.error("{} tried to teleport or move diagonaly -> DEAD".format(snake.agent.name))
            return AgentUpdate.died
        head=(head[0]+snake.agent.direction[0],head[1]+snake.agent.direction[1])
        #wrap the snake around the window
        headx=self.hortiles-1 if head[0]<0 else 0 if head[0]>=self.hortiles else head[0]
        heady=self.verttiles-1 if head[1]<0 else 0 if head[1]>=self.verttiles else head[1]
        head=(headx,heady)
        #update the body and see if the snake is dead
        alivelist=[alive for alive in reversed(self.players) if not alive.IsDead]
        for alive in alivelist:
            if head in alive.body:
                if head == alive.body[0]: #in case of head to head collision, kill both of the snakes
                    if snake.agent.name != alive.agent.name:
                        logging.debug("{} crashed against {} head -> BOTH DEAD".format(snake.agent.name, alive.agent.name))
                        self.gameKill(alive)
                    else:
                        logging.debug("{} crashed against itself -> Suicide...".format(snake.agent.name))
                self.gameKill(snake)
                return AgentUpdate.died
        if head in self.obstacles:#hit an obstacle
            self.gameKill(snake)
            logging.debug("{} crashed against obstacle -> DEAD".format(snake.agent.name))
            return AgentUpdate.died
        elif head == self.foodpos:
            #the snake ate the food
            snake.body.append((snake.body[0]))
            snake.point(10)
            r = AgentUpdate.ate_food
        #the snake hasnot collided....move along
        snake.body=[head]+snake.body[:-1]
        try:
            b = lambda x: x.agent.updateBody(copy.deepcopy(x.body))
            self.timekeep(snake, b)
        except Exception as error:
            logging.error(str(error))
            snake.kill()
        return r
    
    def start(self):
        clock = pygame.time.Clock()
        self.count=0
        while len([p for p in self.players if not p.IsDead]) > 1 and self.count < self.timeout :
            clock.tick(self.fps)
            if self.screen != None:
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == K_q): #close window or press Q
                        pygame.quit();
                        exit()
                    elif event.type == pygame.KEYDOWN:
                        for player in self.players:
                            player.agent.processkey(event.key)
                    elif event.type == pygame.VIDEORESIZE:
                            self.tilesize = int(max(event.w/(self.hortiles), event.h/(self.verttiles)))
                            self.screen = pygame.display.set_mode(((self.hortiles)*self.tilesize,(self.verttiles)*self.tilesize+25), pygame.RESIZABLE)
                self.screen.fill((0,0,0))
            self.count+=1
            #game logic is updated in the code below
            self.updatePlayerInfo()
            
            #moving food
            run = [-1,1,0]
            neighbours = [((self.foodpos[0] + x)%self.hortiles, (self.foodpos[1] + y)%self.verttiles) for x in run for y in run]
            valid_neighbours = [n for n in neighbours if not n in self.obstacles and not n in self.playerpos] 
            self.foodpos = random.choice(valid_neighbours)

            for player in [a for a in self.players if not a.IsDead]:
                try:
                    if player.name == "":
                        sys.exit(1) #player couldn't be initialized

                    maze = Maze(self.obstacles, self.playerpos, self.foodpos)   #just a copy of our information (avoid shameful agents that tinker with the game server)
                    b = lambda x: x.agent.updateDirection(maze)
                    self.timekeep(player, b)
                except Exception as error:
                    raise error
                    player.kill()
            #this variable makes sure both snakes can eat the same food at the same turn 
            someone_ate_food = False
            for player in self.players:
                if self.update(player) == AgentUpdate.ate_food:
                    someone_ate_food = True
            if someone_ate_food: 
                self.generateFood()
 
            #print all the content in the screen
            if self.screen != None:
                for player in self.players: #print players
                    #head + rest of body
                    pygame.draw.rect(self.screen, player.head_color, (player.body[0][0]*self.tilesize,player.body[0][1]*self.tilesize,self.tilesize,self.tilesize),0)
                    for part in player.body[1:]:
                        pygame.draw.rect(self.screen, player.color, (part[0]*self.tilesize,part[1]*self.tilesize,self.tilesize,self.tilesize),0)

                for obstacle in self.obstacles: #print obstacles
                    pygame.draw.rect(self.screen,self.obscolor,(obstacle[0]*self.tilesize,obstacle[1]*self.tilesize,self.tilesize,self.tilesize),0)

                #print food
                pygame.draw.rect(self.screen,self.foodcolor,(self.foodpos[0]*self.tilesize,self.foodpos[1]*self.tilesize,self.tilesize,self.tilesize),0)
 
            self.printstatus()
            if self.screen != None:
                pygame.display.update()

        logging.info("GAME OVER after {} counts".format(self.count))
        #print(max(self.players, key=lambda p: p.points).name)
        for p in self.players:
            try:
                p.agent.destroy()
            except Exception as error:
                logging.error(str(error))

        while self.screen != None:
            event = pygame.event.wait()
            if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == K_q): #close window or press Q
                pygame.quit(); 
                exit()
