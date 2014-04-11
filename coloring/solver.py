#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
import sys
import time
sys.setrecursionlimit(10000) # 10000 is an example, try with different values

# colorsys.hsv_to_rgb(.5,.5,.4)
import colorsys

class Node:
    def __init__(self,i):
        self.neighbors = []
        self.color = -1
        self.id = i

    @staticmethod
    def nodesFromEdges(edges, node_count):
        nodes = [ Node(x) for x in range(node_count) ]
        for (l,r) in edges:
            nodes[l].neighbors.append(nodes[r])
            nodes[r].neighbors.append(nodes[l])
        for node in nodes:
            node.degree = len(node.neighbors)
        # need to update neighbors too and indices too, dummy
        # nodes.sort(lambda na,nb: nb.degree - na.degree)
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
        self.render = GraphRender()
    
    def freeColors(self, node, num_colors):
        free_colors = {}.fromkeys(range(num_colors))
        for neighbor in node.neighbors:
            if neighbor.color < 0 or not neighbor.color in free_colors:
                continue
            free_colors.pop(neighbor.color)
        return free_colors.keys()

import argparse
from collections import namedtuple
ColoredResult = namedtuple("Result", ['numColors', 'nodes', 'opt'])

def color_from_color_id(color_id):
    # use palette, apparently a straight number will just work
    # nice thing about this: colors stay same as num_colors changes
    if color_id < 0:
        return "#ffffff"
    return str(10+max(color_id+1,0))

    # or use hsv
    if color_id < 0:
        return "888888" # grayish
    value = float(color_id)/float(num_colors + 1)
    return "#"+"".join(map(lambda x: "%.2X" % x, map(lambda x: int(x*255), colorsys.hsv_to_rgb(value,1,1))))

class GraphRender:
    def __init__(self):
        self.render_nodes = None
        import ubigraph
        self.U = ubigraph.Ubigraph()
        self.styles = {}

    def render(self, nodes):
        # set up the render state
        if not self.render_nodes:
            self.U.clear()
            self.render_nodes = [self.U.newVertex() for node in nodes]
            for node in nodes:
                for neighbor in node.neighbors:
                    self.U.newEdge(self.render_nodes[node.index], self.render_nodes[neighbor.index])        

        for node in nodes:
            if not node.color in self.styles:
                color = color_from_color_id(node.color)
                print "making style:",color
                self.styles[node.color] = self.U.newVertexStyle(shape="sphere", color=color)
            self.render_nodes[node.index].set(style=self.styles[node.color], label=str(node.index))
    

def solve_node(state, node_i, num_colors, min_result):
    # give up after a period of time
    if state.end_time and time.time() >= state.end_time:
        min_result.opt = False
        return min_result

    # no point in descending, num_colors can only go up
    if min_result.numColors <= num_colors:
        # print "min result better, returning",num_colors, min_result.numColors
        # render
        return min_result

    # all nodes colored, must be a better solution
    if node_i == state.nodeCount:
        #print "new best result",num_colors, node_i
        res = ColoredResult(num_colors, copy.deepcopy(state.nodes), 1)
#        state.render.render(res.nodes)
        return res

    # we only get to this part if we're on a path to fewer 
    # colors than an existing solution 

    node = state.nodes[node_i]

    free_colors = state.freeColors(node,num_colors)
    to_try = [(color, num_colors) for color in free_colors]
    to_try.append((num_colors,num_colors+1))
    would_have_broken_out = False
    for color, n_colors in to_try:
        node.color = color

        # render
#        import time
#        state.render.render(state.nodes)
#        time.sleep(1)

        res = solve_node(state, node_i+1, n_colors, min_result)
        if res.numColors < min_result.numColors:
            #print node_i, "new best result:", res.numColors
            min_result = res
    node.color = -1
    return min_result

def solve_greedy(edges, node_count):
    state = State(edges, node_count)
    # sort by most to least constrained
    state.nodes.sort(lambda a, b: len(b.neighbors) - len(a.neighbors))
    state.end_time = time.time() + 60
    (sln_num_colors, sln_nodes, opt) =  solve_node(state, 0, 0, ColoredResult(sys.maxint, [], 0))
    
    # undo sort
    res_nodes = [None] * len(sln_nodes)
    for n in sln_nodes:
        res_nodes[n.id] = n
        
    return ColoredResult(sln_num_colors, res_nodes, opt)

def solve_it_greedy(edges, node_count):
#    state.render.render(res.nodes)
    res = solve_greedy(edges, node_count)
    return (res.numColors, [ n.color for n in res.nodes ], res.opt)

ColorClass = namedtuple("Class", ['color', 'nodes'])


class Kempe:
    """
    takes a solution to the coloring problem and optimizes it
    """

    def __init__(self, nodes, node_count):
        self.nodes = copy.deepcopy(nodes)
        self.node_count = node_count
        for node in self.nodes:
            if node.color < 0:
                raise Exception('all nodes must be colored')

    def calcColorClasses(self):
        # figure out color classes
        num_colors = len({node.color:None for node in self.nodes})
        color_classes_small_to_big = [ColorClass(i,[]) for i in range(num_colors)]
        for node in self.nodes:
            color_classes_small_to_big[node.color].nodes.append(node)
        return color_classes_small_to_big

    def calcColorClassesSmallToBig(self):
        # sort by smallest to largest
        color_classes_small_to_big = self.calcColorClasses()
        color_classes_small_to_big.sort(lambda ca, cb: len(ca.nodes) - len(cb.nodes))
        return color_classes_small_to_big

    def calcColorClassesBigToSmall(self):
        # sort by smallest to largest
        color_classes_big_to_small = self.calcColorClassesSmallToBig()
        color_classes_big_to_small.reverse()
        return color_classes_big_to_small

    def calcNewNodeColor(self, node):
        color_classes = self.calcColorClassesBigToSmall()
        for color_class in color_classes:
            if color_class.color != node.color:
                return color_class.color

    def canRecolorNode(self, node, new_color):
        for n in node.neighbors:
            if n.color == new_color:
                return False
        return True

    def recolorNode(self, node, color_classes_big_to_small):
        """Find a new color for this node if possible, return True or False
        """
        for (cls_color, cls_nodes) in color_classes_big_to_small:
            if cls_color != node.color and self.canRecolorNode(node, cls_color):
                node.color = cls_color
                return True
        return False

    def removeColorClass(self, color, nodes):
        """Try to remove a color class from the state by finding any other colors to switch to
        """
        # try putting this node in a different color class
        color_classes_big_to_small = self.calcColorClassesBigToSmall()
        res = True
        for node in nodes:
            if not self.recolorNode(node, color_classes_big_to_small):
                res = False
        return res
            
    def reduce(self):
        class_to_try = 0
        while True:
            color_classes_small_to_big = self.calcColorClassesSmallToBig()
            if class_to_try >= len(color_classes_small_to_big):
                break
            (color, nodes) = color_classes_small_to_big[class_to_try]
            if self.removeColorClass(color, nodes):
                class_to_try = 0
                # compact the colors
                for node in self.nodes:
                    if node.color > color:
                        node.color -= 1
            else:
                class_to_try += 1

def solve_it_kempe(edges, node_count):
    greedy = solve_greedy(edges, node_count)

    if greedy.opt:
        return greedy

    # print 'HACK! remove'
    # nodes[0].color = num_colors
    # num_colors += 1

    kempe = Kempe(nodes, num_colors)
    kempe.reduce()
    return (len(kempe.calcColorClasses()), [node.color for node in kempe.nodes], 0)
    
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
    #(num_colors, solution, opt) = solve_it_greedy(edges, node_count)
    (num_colors, solution, opt) = solve_it_kempe(edges, node_count)

    # prepare the solution in the specified output format
    output_data = str(num_colors) + ' ' + str(opt) + '\n'
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
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        print solve_it_file(sys.argv[1].strip())
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)'

