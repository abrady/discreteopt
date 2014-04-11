#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight'])

# python -m cProfile ./solver.py ./data/ks_30_0

parser = argparse.ArgumentParser(description='Process some integers.')
#parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                   help='an integer for the accumulator')
parser.add_argument("-d", "--dynamic", help="run the dynamic solution", action="store_true")
parser.add_argument('filename')

args = parser.parse_args()


# idea of the grid:
# 
#   0 1 2 3 ...
# 0 0 0 0 0
# 1 0 0 1 1
# 2 0 2 2 2
# 3 0 2 3 3
# 4 0 2 3 4
# ---------
#     2 1 3
# pseudo:
# at each item i, at each weight k from 0 to capacity figure out if I should take this item or not:
# foreach i from 0 to len(items):
#  foreach k from 0 to capacity:
#   if value_with > value_without:
#     values[i][k] = value_with
#   else:
#     values[i][k] = value_without
#   where:
#     value_without = values[i-1][k]
#     value_with = 0 if items[i].weight > capacity else values[i-1][k-weight_with]
# 
def dynamic_sln(items, capacity):
    # prebuild the array of values (not strictly necessary)
    values = [[0 for k in range(capacity + 1)] for i in range(len(items))]

    # print values
    for i in range(len(items)):
        for k in range(capacity + 1):
            item = items[i];
            value_without = 0
            if i > 0:
                value_without = values[i-1][k]

            # see if we can fit this item in the bag
            # and calculate the optimal value
            value_with = 0
            if item.weight <= k:
                # we have room. shove this item in, and get the value
                # of the optimal solution for a bag that is smaller by
                # the weight of this item
                # print "prev optimal:",values[i-1][k-item.weight]
                value_with = item.value + values[i-1][k-item.weight]
            
            # see if sticking this item in actually increased the 
            # value of the contents vs. leaving it out
            # print "item",i,"weight",item.weight,"values with and w/o", value_with, value_without
            values[i][k] = max(value_with, value_without)

    # now we have the optimal solution in values:
    # 

    # first get the optimal solution
    k = capacity
    opt_value = values[len(values)-1][k]
    chosen = []

    # figure out which ones were chosen
    # easy to do because their value at k 
    # would increase if chosen
    # print values, k
    for i in range(len(items)-1,-1,-1):
        # item zero is a little trickier. I could pad the values matrix with a 'zeroes' 
        # column or just check this here and set it to zero.
        prev_value = values[i-1][k] if i > 0 else 0
        if values[i][k] != prev_value:
            chosen.append(1)
            k = k - items[i].weight
        else:
            chosen.append(0)
    chosen.reverse()
    return (opt_value, chosen)

# use a linear relaxation so that instead of adding or not adding
# the item to the knapsack, we break up the items.
# then what we do is we see if, by breaking up the items
# we can get a value greater than our highest seen value, and if we
# can't we know we don't need to explore this path any longer
#
# certainly a way to optimize this: we calculate every range twice
def _relaxed_value(relaxed_values, items, capacity, j):
    value = 0
    weight = 0
    i = j

    if (capacity, j) in relaxed_values:
        return relaxed_values[(capacity, j)]

    for i in range(j, len(items)):
        item = items[i]
        if weight + item.weight > capacity:
            break
        weight += item.weight
        value += item.value
    # reached the end, done
    if i == len(items):
        return value
    # calc fractional value of next item
    fractional_weight = float(capacity - weight)/items[i].weight
    fractional_value = items[i].value*fractional_weight
    value += int(fractional_value) # round down should be fine here.

    relaxed_values[(capacity, j)] = value
    return value

def relax_branch_bound_sln(items, capacity):
    # first sort the items by weighted value
    # e.g. y.value/y.weight > x.value/x.weight, but being a little tricky
    # due to integer math
    items = items[:]
    items.sort(lambda x, y: y.value*x.weight - x.value*y.weight) 

    relaxed_values = {}
    stack = []
    value_max = 0
    # every item pushed off the stack is a choice about that item:
    # push 
    chosen_accum = [0 for i in items]
    chosen_max = []

    # push the first two items inclusive and exclusive
    stack.append((0,0,0,False))
    stack.append((0,0,0,True))

    # starting with the first item:
    # - calculate relaxed value given current state
    # - if relaxed value < current best value, skip
    # - add/don't add item, accumulate, and descend
    while(len(stack) > 0):
        (i, value_accum, weight_accum, chosen) = stack.pop()
        # print i,value_accum,weight_accum
        
        # terminate
        #########
        if i >= len(items):
            # see if we have a new max value
            if value_accum > value_max:
                value_max = value_accum
                chosen_max = chosen_accum[:]
            continue

        # current item
        #########

        item = items[i]

        # track the state on the way down
        chosen_accum[item.index] = chosen

        # descend
        ##########

        # figure out the maximum possible value we could get with the remaining space
        # if it is smaller than a max value we've already seen, bail out
        relaxed_val = value_accum + _relaxed_value(relaxed_values, items, capacity - weight_accum, i)
        if relaxed_val < value_max:
            continue # we've seen a sack with greater value than this

        stack.append((i+1,value_accum, weight_accum, False)) # without

        if item.weight + weight_accum > capacity:
            continue # out of room

        stack.append((i+1,value_accum + item.value, weight_accum + item.weight, True)) # with item
    chosen_final = [ 0 for i in items ]
    # goofy shit to get the unsorted indexes out
    for i in range(len(chosen_max)):
        if chosen_max[i] == 1:
            item = items[i]
            chosen_final[item.index] = 1
    return (value_max, chosen_final)


def test_items():
    items = []
    capacity = 11

    items.append(Item(0, 8, 4))
    items.append(Item(1, 10, 5))
    items.append(Item(2, 15, 8))
    items.append(Item(3, 4, 3))
    return (items, capacity)

def test_branch_bound():
    return relax_branch_bound_sln(*test_items())

def test_dyn():
    return dynamic_sln(*test_items())

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))

    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    value = 0
    weight = 0
    taken = [0]*len(items)

    if args.dynamic:
        # print "dynamic"
        (value, taken) = dynamic_sln(items, capacity)
    else:
        # print "branch bound"
        (value, taken) = relax_branch_bound_sln(items, capacity)
    
    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


import sys

def solve_it_file(file_location):
    input_data_file = open(file_location, 'r')
    input_data = ''.join(input_data_file.readlines())
    input_data_file.close()
    return solve_it(input_data)

if __name__ == '__main__':
    if len(args.filename):
        print solve_it_file(args.filename)
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)'

