#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
import copy
import sys
import time
import itertools
sys.setrecursionlimit(10000) # 10000 is an example, try with different values

Point = namedtuple("Point", ['x', 'y'])
Path = namedtuple("Path", ['length', 'path'])
d_ = None
d_closest = None

import networkx as nx
import matplotlib.pyplot as pl
class GraphRenderer:
    def __init__(self, points):
        self.G = nx.Graph()
        self.G.add_nodes_from(range(len(points)))
        self.pos = {}
        for i in range(len(points)):
            self.pos[i] = (points[i].x, points[i].y)

    def draw_path(self, path):
        edges = path_edges(path.path)
        self.G.add_edges_from(edges)
        nx.draw(self.G, self.pos)

    def draw_difference(self, path_old, path_new):
        self.draw_path(path_old)
        H = self.G.copy()
        H.add_edges_from(path_edges(path_new.path))
        H_ = nx.difference(self.G, H)
        nx.draw(self.G, self.pos)
        nx.draw(H_, self.pos, edge_color='blue')

    @staticmethod
    def show():
        pl.show()        
        

def solve_it_bruteforce(points, greedy=False):
    min_result = Path(sys.maxint, [])
    for candidate_path in itertools.permutations(range(len(points))):
        length = path_length(points, candidate_path)
        if length < min_result.length:
            # print "greedy new shortest path:",length,candidate_path
            min_result = Path(length, candidate_path)
            if greedy:
                break
    return min_result

def swap_path_points(points,path,i,j):
    mid = path[i:j+1][::-1] # reverse mid
    path_ = path[0:i]+mid+path[j+1:]
    return path_

def find_best_swap(points, s, i):
    """find the best neighbor to swap node i with
    """
    for j in range(i+1,len(s.path)):
        path_ = swap_path_points(points, s.path, i, j)
        length_ = path_length(points, path_)
        if length_ < s.length:
            # print i,",",j,": new shortest path: ", length_, ", path: ",path_
            s = Path(length_, path_)
    return s
        
def solve_it_bestswap(points):
    """solve TSP by swapping. how expensive? n-1 + n-2 + n-3 + ... + n-n : n*n - sum(1 to n) = n(n-1)/2
    not great, but pretty good
    """
    renderer = GraphRenderer(points)
    s = solve_it_bruteforce(points, greedy=True)
#    renderer.draw_path(s)
#    renderer.show()
    length_last = None
    while not length_last or length_last > s.length:
        length_last = s.length
        for i in range(len(s.path)-2):
            s_ = find_best_swap(points, s, i)
            if s_.length < s.length:
                GraphRenderer(points).draw_difference(s, s_)
#                GraphRenderer(points).draw_path(s_)
                GraphRenderer.show()
                s = s_
    return s

def path_edges(path):
    return [(path[i], path[(i+1)%len(path)]) for i in range(len(path))]

def path_length(points, path):
    res_length = 0
    path_steps = path_edges(path)
    for i0, i1 in path_steps:
        res_length += d_[i0][i1]
    return res_length

def longest_edge_indexes(points):
    global d_
    max_edge_idxs = None
    max_d = 0
    for i in range(len(points)):
        j = (i+1)%len(points)
        a,b = points[i],points[j]
        if d_[a][b] > max_d:
            max_edge_idxs = (i,j)
    return max_edge_idxs

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def examine_swap(points, path,path_length,a,b,c):
    """examine the benefit of swapping a-b with a-c
    """
    node_d = (a.index(c)+1)%len(points)
    _path_length = path_length - d_[a][b] - d_[c][node_d]+ d_[a][c] + d_[b][c]
    if _path_length < path_length_best:
        path_length_best = _path_length
        swaps_best = swaps_accum + [c]

def calc_best_kopt_for_node(points, path, i):
    """determine the most beneficial swap for 2 to nopt
    """
    path_len_min = path_length(points, path)
    path_len_ = path_len_min
    path_min = path

    print "starting",path
    j = (i+1)%len(path)
    for kopt in range(10):
        a = path[i]
        b = path[j]
        c = d_closest[b][0]
        if d_[b][c] >= d_[a][b]:
            print "not any closer, quitting"
            break
        # we're pointing b to its closest neighbor c, a will point to c's previous node
        l = (path.index(c)-1)%len(path)
        d = path[l]
        path_len_ = path_len_ - d_[a][b] - d_[c][d] + d_[a][d] + d_[b][c]
        path = swap_path_points(points, path, j, l)
        if path_len_ != path_length(points, path):
            raise Error("path lengths don't match",path_len_, path_length(path))
        print "new path",path,"from swapping(",a,',',b,') with (',d,',',c,') len',path_len_
        if path_len_ < path_len_min:
            path_len_min = path_len_
            path_min = path[:]

    return Path(path_len_min, path_min)

def solve_it_kopt(points):
    """gist of this algo:
    - explore swaping edges to see if it reduces cost, if you do one swap it may not help that much, but swapping again and again may.
    example:
path is 1,2,3,4,5. swap edge 1-2 with edge 3-4, now path is 1,3,2,4,5 is that better? next, see if the 1-3 edge can be swapped for something better: 1-4. now path is 1,4,2,3,5, better? track the cost and keep digging
    """
    s = solve_it_bruteforce(points, greedy=True)
    r = calc_best_kopt_for_node(points, s.path, 0)
    print "best kopt", r
    return r

def parse_input_file(file_location):
    input_data_file = open(file_location, 'r')
    input_data = ''.join(input_data_file.readlines())
    input_data_file.close()
    return parse_input(input_data)

def parse_input(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))
    points = tuple(points) # make immutable

    return (nodeCount, points)

# 5_1: 4.0 0
# 10_1: 159.477145493 0\n0 1 6 7 4 8 3 9 2 5
def solve_it(fn):
    (nodeCount, points) = parse_input_file(fn)
    # build a trivial solution
    # visit the nodes in the order they appear in the file
    # solution = range(0, nodeCount)
    global d_, d_closest
    d_ = [[ length(p0, p1) for p1 in points ] for p0 in points]
    d_closest = [[ (neighbors[i], i) for i in range(len(neighbors))] for neighbors in d_]
    [ pdist.sort() for pdist in d_closest ]
    d_closest = [ [n[1] for n in neighbors] for neighbors in d_closest]
    # remove self as closest neighbor
    for neighbors in d_closest:
        neighbors.pop(0)

    # solution = solve_it_bruteforce(points, greedy=True).path
    #solution = solve_it_bestswap(points).path
    solution = solve_it_kopt(points).path

    # calculate the length of the tour
    obj = length(points[solution[-1]], points[solution[0]])
    for index in range(0, nodeCount-1):
        obj += length(points[solution[index]], points[solution[index+1]])

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

# 51: 1173.09125468
def solve_it_file(file_location):
    return solve_it(file_location)

import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print solve_it_file(sys.argv[1])
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)'

