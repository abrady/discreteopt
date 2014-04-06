#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy

class Node:
    def __init__(self,i):
        self.neighbors = []
        self.color = -1
        self.index = i

    @staticmethod
    def nodesFromEdges(edges, node_count):
        nodes = [ Node(x) for x in range(node_count) ]
        for (l,r) in edges:
            nodes[l].neighbors.append(nodes[r])
            nodes[r].neighbors.append(nodes[l])
        for node in nodes:
            node.degree = len(node.neighbors)
        nodes.sort(lambda na,nb: na.degree - nb.degree)
        return nodes

    def __repr__(self):
        return "Node("+str(self.color)+", "+str([n.index for n in self.neighbors])+")"

    def __str__(self):
        return str(self.color)

class State:
    def __repr__(self):
        return "State("+str(self.nodes)+')'
    
    def __init__(self, edges, node_count):
        self.nodes = Node.nodesFromEdges(edges, node_count)
        self.uncolored = self.nodes
        self.nodeCount = node_count
        self.greedy = False
        
        self.colored = []
        self.max_degree = max([len(n.neighbors) for n in self.nodes])
    
    def freeColors(self, node, num_colors):
        free_colors = {}.fromkeys(range(num_colors))
        for neighbor in node.neighbors:
            if neighbor.color < 0 or not neighbor.color in free_colors:
                continue
            free_colors.pop(neighbor.color)
        return free_colors.keys()

import argparse
from collections import namedtuple
ColoredResult = namedtuple("Result", ['numColors', 'nodes'])
 
def solve_node(state, node_i, num_colors, min_result):
    if state.greedy:
    # no point in descending, num_colors can only go up
    if min_result.numColors <= num_colors:
        #print "min result better, returning",num_colors, min_result.numColors
        return min_result

    # all nodes colored, check for new better solution
    if node_i == state.nodeCount:
        print "new best result",num_colors, node_i
        return ColoredResult(num_colors, copy.deepcopy(state.nodes))

    # we only get to this part if we're on a path to fewer 
    # colors than an existing solution 

    node = state.nodes[node_i]

    free_colors = state.freeColors(node,num_colors)
    to_try = [(color, num_colors) for color in free_colors]
    to_try.append((num_colors,num_colors+1))
    would_have_broken_out = False
    for color, n_colors in to_try:
        node.color = color
        res = solve_node(state, node_i+1, n_colors, min_result)
        if res.numColors < min_result.numColors:
            #print node_i, "new best result:", res.numColors
            min_result = res
    node.color = -1
    return min_result

def solve_it_recurrance(edges, node_count):
    state = State(edges, node_count)
    res = solve_node(state, 0, 0, ColoredResult(sys.maxint, []))
    return (res.numColors, [ n.color for n in res.nodes ])
    
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
    # solution = solve_it_greedy(edges, node_count)
    (num_colors, solution) = solve_it_recurrance(edges, node_count)

    # prepare the solution in the specified output format
    output_data = str(num_colors) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


# gc_20_1: 3
# gc_20_3: 5
# gc_20_5: 5
# gc_20_7: 8
# gc_20_9: 11

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

