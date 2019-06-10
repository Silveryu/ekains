from snake import Snake
from constants import *
from search import *
import copy
#TODO:
# n se encurralar

#####################################################################

FREE = 0
EXPLORED = -1
OBS = 1

class StudentAgent(Snake):

    def __init__(self, body=[(0, 0)], direction=(1, 0),name="snaIQ"):
        super().__init__(body, direction, name=name)
        self.path = None
        self.explored = set()
        self.original_dist = 0

    def update(self, points=None, mapsize=None, count=None, agent_time=None):
        # [(agent1.name,agent1.points),...]
        #self.points = points

        # (hortiles,verttiles)
        self.mapsize = mapsize

        # Numero de "jogadas"
        self.count = count

        # time in ms
        self.agent_time = agent_time

        # inicializar mapa usado uma grid
        if self.count == 1:
            self.grid = { (x,y):0 for x in range(mapsize[0]) for y in range(mapsize[1])}


    def updateDirection(self, maze):
        # Maze contains:
        # maze.obstacles -> [(, ),(, )]
        # maze.playerpos (positions occupied by players)-> [(, ),(, )]
        # maze.foodpos -> (, )
        #inicializar grid com obstaculos
        self.start = pygame.time.get_ticks()

        if self.count == 1:
            self.foodpos = maze.foodpos
            for obs in maze.obstacles:
                self.grid[obs] = OBS
            self.fillGrid()

        # direcção geral do obstaculo mudou, o caminho precisa de ser recalculado

        if self.has_jumped(self.foodpos,maze.foodpos):
            self.path = None
            self.original_dist = 0
            for pos in self.explored:
               self.grid[pos] = FREE
            self.explored = set()


        problem = SnakeProblem(self.body,maze,self.mapsize,self.direction,self.grid,self.agent_time)

        if not self.path or len(self.path) < 0.2 * self.original_dist:

            self.get_path(problem,True)

        if self.path and len(self.path)>= 1:

            n_dir = self.path.pop(0)
            #simple adv colision avoidance
            if not n_dir in problem.actions(problem.initial,self.direction):
                self.get_path(problem)
                if self.path:
                    n_dir = self.path.pop(0)

            if problem.result(problem.initial,n_dir) in problem.get_adv_next_p_head():
                self.get_path(problem)
                if self.path:
                    n_dir = self.path.pop(0)
            if self.path:
                self.direction = n_dir

        if not self.path:
            p_actions = problem.actions(self.body[0], problem.cur_dir)
            if p_actions:
                self.direction = p_actions[0]

        self.foodpos = maze.foodpos

    def result(self, state, action):
        return ((state[0] + action[0]) % self.mapsize[0], (state[1] + action[1]) % self.mapsize[1])

    def get_path(self,problem,replace_original_dst = False):
        search_prob = Search(problem)

        self.node = search_prob.search(self.start)

        if self.node:
            self.path = self.node.solution()
            if replace_original_dst:
                self.original_dst = len(self.path)

        for pos in search_prob.explored:
            self.grid[pos] = EXPLORED

        self.explored.update(search_prob.explored)


    def has_jumped(self,original_food_pos, new_food_pos):
        dx = abs(original_food_pos[0] - new_food_pos[0])
        dy = abs(original_food_pos[1] - new_food_pos[1])

        return min(dx, self.mapsize[0] - dx) > 1 or min(dy, self.mapsize[1] - dy) > 1

    def fillGrid(self):
        free_pos = [ pos for pos in self.grid if self.grid[pos] != OBS ]

        for pos in free_pos:
            #if we need to check for deadends
            checkFlag = 1

            checking_pos = pos
            while(checkFlag):

                checkFlag = 0
                # list with surrounding positions that are free
                #posições livres
                surr_free_lst = self.surrounding_free_pos(checking_pos)
                # needs to be closed
                if len(surr_free_lst) <= 1:
                    self.grid[checking_pos] = OBS

                if len(surr_free_lst) == 1:
                    checkFlag = 1
                    checking_pos = surr_free_lst[0]



    def surrounding_free_pos(self,pos):

        return [self.result(pos,p_dir) for p_dir in directions if
                    self.grid[self.result(pos, p_dir)] != OBS]
