from constants import *
class Node:

    def __init__(self, state, parent=None, action=None, path_cost=0):
        "Create a search tree Node, derived from a parent by an action."
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    def __repr__(self):
        return "<Node %s>" % (self.state,)

    # used when two nodes have same f evaluation result
    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        return [self.child_node(problem, action) \
                for action in problem.actions(self.state, self.action) ]


    def child_node(self, problem, action):

        next = problem.result(self.state, action)

        return Node(next, self, action, \
                    problem.path_cost(self.path_cost, self.state,action, next))

    def solution(self):
        return [node.action for node in self.path()[1:]]

    # return list with all nodes in path to goal state
    def path(self):
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state