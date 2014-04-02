#!/usr/bin/python
# -*- coding: utf-8 -*-

def make_node_neighbors(edges):
    max_neighbor = reduce(max, map(max, edges))
    node_neighbors = [ {} for x in range(max_neighbor+1) ]
    for l,r in edges:
        node_neighbors[l][r] = l
        node_neighbors[r][l] = r
    return node_neighbors

def is_solution(node_colors, node_neighbors):
    for i in range(len(node_colors)):
        color = node_colors[i]        
        for n in node_neighbors[i]:
            if color == node_colors[n]:
                return False
    return True

def solve_it_recurrance(edges, node_count):
    '''
    Quick and dirty recurrance solution. this just tries a color and then makes
    sure all the states are valid
    '''
    node_colors = [ 0 for x in range(node_count)]
    node_neighbors = make_node_neighbors(edges)
    colored_nodes = 0
    while True:
        # increment the color
        # if a node wraps around, increment the next node's color
        i = 0
        for i in range(node_count):
            node_colors[i] += 1
            if node_colors[i] < 4:
                break
            node_colors[i] = 0

        # safety check
        if i == node_count:
            print "no solution, shouldn't happen"
            return []

        # check solution
        if is_solution(node_colors, node_neighbors):
            return node_colors
    print "returning at end?"

class Node:
    def __init__(self):
        self.neighbors = []
        self.color = 0

    @staticmethod
    def nodesFromEdges(edges, node_count):
        nodes = [ Node() for x in range(node_count) ]
        for (l,r) in edges:
            nodes[l].neighbors.append(r)
            nodes[r].neighbors.append(l)
        return nodes

    def __repr__(self):
        return "Node("+str(self.color)+", "+str(self.neighbors)+")"

    def __str__(self):
        return str(self.color)

class State:
    def __repr__(self):
        return "State("+str(self.nodes)+", "+str(self.stack)+")"
    
    def __init__(self, edges, node_count):
        self.nodes = Node.nodesFromEdges(edges, node_count)
        self.stack = []

    def isSolution(self):
        for node in self.nodes:
            if node.color == 0:
                return False # incomplete
            for neighbor in [ nodes[i] for i in node.neighbors ]:
                if node.color == neighbor.color:
                    return False
        return True

    def pickNode(self):
        res = None
        for node in self.nodes:
            if node.color == 0:
                res = node
                break
        self.stack.append(res)
        return res

    def assignNodeColor(self, node):
        neighbor_colors = {self.nodes[i].color:True for i in node.neighbors}
        color = 1
        while neighbor_colors.has_key(color):
            color += 1
        node.color = color

    def backTrack(self):
        node = self.stack.pop()
        node.color = 0;
        return self

def solve_it_propogation(edges, node_count):
    '''The idea of this approach is to have a constraint system that is updated
    with choices made by the search component. In the case of graph coloring:
    the constraints are that picking a color reduces the choices of its neighbors colors

    This is just a dumb greedy algorithm
    '''
    state = State(edges, node_count)
    
    # pick a node
    # assign color
    # update neighbors
    # detect failure
    # search algo: 
    while True:
        node = state.pickNode() # get an uncolored node
        if not node:
            break
        # pick a color to try
        state.assignNodeColor(node)

    res = [ n.color - 1 for n in state.nodes ]
    return res

    
def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    # build a trivial solution
    # every node has its own color
    # solution = range(0, node_count)
    # solution = solve_it_recurrance(edges, node_count)
    solution = solve_it_propogation(edges, node_count)

    # prepare the solution in the specified output format
    output_data = str(node_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def solve_it_file(fn):
    file_location = fn
    input_data_file = open(file_location, 'r')
    input_data = ''.join(input_data_file.readlines())
    input_data_file.close()
    return solve_it(input_data)
    
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print solve_it_file(sys.argv[1].strip())
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)'

