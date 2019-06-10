from constants import *
from node import Node
from priorityqueue import PriorityQueue
import pygame

class SnakeProblem:


    def __init__(self, body, maze, mapsize, cur_dir, grid, time = None):
        #states are tuples with pos
        self.body = body
        self.initial = body[0]
        self.goal = maze.foodpos
        self.maze = maze
        self.mapsize = mapsize
        self.grid = grid
        self.cur_dir = cur_dir
        self.possible_actions = { up: [left, up, right],
                                  down: [left, down, right],
                                  left: [up, down, left],
                                  right: [down, up, right] }
        self.time = time
        self.playerpos = self.maze.playerpos + self.get_adv_next_p_head()

    # Actions will be a list of directions
    # Logic of avoiding objects parcially treated here

    def actions(self, state, last_action):
        p_dir = self.possible_actions[last_action]

        return [ n_dir for n_dir in p_dir if self.grid[self.result(state, n_dir)] != 1 and
                 self.result(state, n_dir) not in self.playerpos ]

    def result(self, state, action):

        return ( (state[0] + action[0]) % self.mapsize[0], (state[1] + action[1]) % self.mapsize[1] )

    def goal_test(self, state):

        return state == self.goal

    def path_cost(self, c, state1, action, state2):

        return c + 1

    # Using manhattan distance
    # adapted to current problem
    def heuristic(self,node):

        dx = abs(self.goal[0] - node.state[0])
        dy = abs(self.goal[1] - node.state[1])
        # altered heuristic to make the snake go straight
        dir_h = (node.action != node.parent.action) * 0.0001 if node.parent else 0
        # explored heuristic
        exp_h = (self.grid[node.state] == -1)*0.001
        return (min(dx, self.mapsize[0] - dx) + min(dy, self.mapsize[1] - dy) + exp_h + dir_h )* (1 + 1/30)

    def get_adv_next_p_head(self):

        player_pos = self.maze.playerpos

        if self.body[0] == player_pos[0]:
            adv_body = player_pos[len(self.body):]
        else:
            adv_body = player_pos[:len(self.body)]

        adv_head = adv_body[0]
        poss_head = []

        for dir in directions:
            poss_head.append(self.result(adv_head, dir))

        return poss_head



class Search:

    def __init__(self,problem):
        self.explored = set()
        self.f = lambda n: n.path_cost + problem.heuristic(n)
        self.problem = problem

    # f is evaluation function
    # é tratado aqui a deteção de colisões com outros agentes e ele próprio
    def search(self,start):

        node = Node(self.problem.initial,action = self.problem.cur_dir)

        if self.problem.goal_test(node.state):
            return node

        frontier = PriorityQueue(self.f)

        frontier.append(node)

        while frontier:

            node = frontier.pop()

            finish = pygame.time.get_ticks()
            #se demorou 90 % do tempo
            if finish-start >= 0.9*self.problem.time:
                frontier.append(node)
                return node

            if self.problem.goal_test(node.state):
                return node

            self.explored.add(node.state)

            for child in node.expand(self.problem):

                if child.path_cost == 1 and child.state in self.problem.get_adv_next_p_head() :
                    continue

                if child.state not in self.explored and child not in frontier:

                    frontier.append(child)

                # caso o node expandido ja estiver na frontier
                # fica na frontier o que tiver menor função de avaliação
                elif child in frontier:
                    incumbent = frontier[child]
                    if self.f(child) < self.f(incumbent):
                        del frontier[incumbent]
        return None



