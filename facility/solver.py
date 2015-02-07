#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
import itertools

Data = namedtuple("Data", ['facilities', 'customers','d'])
Solution = namedtuple("Sln",['used', 'solution'])
Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location','closest_facilities'])


def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it_bruteforce(data):
    '''for each facility we either open it or not, then figure out the cost
    '''
    # pick which facilities to open
    customer_facilities_best = None
    cost_best = sys.maxint
    for facilities_state in itertools.product([0,1], repeat=len(data.facilities)):
        # assign people to facilities
        open_facilities = {}
        for i in range(len(facilities_state)):
            if facilities_state[i] == 1:
                open_facilities[i] = 0
        if len(open_facilities.keys()) == 0:
            continue
        # just assign the closest people to the closest warehouse
        # probably not brute force optimal
        customer_facilities = [None]*len(data.customers)
        for customer in data.customers:
            def assign_customer():
                for dist,i in customer.closest_facilities:
                    if i not in open_facilities:
                        continue
                    capacity = data.facilities[i].capacity - open_facilities[i]
                    if capacity < customer.demand:
                        continue
                    open_facilities[i] += customer.demand
                    customer_facilities[customer.index] = i
                    break
            # assign customer
            assign_customer()

        if customer_facilities.count(None) > 0:
            # not all customers placed, over capacity likely
            continue
        # all customers assigned, see if new cost is better
        facility_cost = sum([data.facilities[i].setup_cost for i in open_facilities.keys()])
        customer_cost = sum(open_facilities.values())
        cost_ = facility_cost + customer_cost
        # print "trying:",cost_, facilities_state, customer_facilities
        if cost_ < cost_best:
            cost_best = cost_
            customer_facilities_best = customer_facilities[:]
            facilities_state_best = facilities_state[:]
            # print "new best cost:",cost_,facilities_state_best, customer_facilities_best
    
    return (facilities_state_best, customer_facilities_best)


def solve_it_example(data):
    facilities, customers, d_ = data
    # build a trivial solution
    # pack the facilities one by one until all the customers are served
    solution = [-1]*len(customers)
    capacity_remaining = [f.capacity for f in facilities]

    facility_index = 0
    for customer in customers:
        if capacity_remaining[facility_index] >= customer.demand:
            solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand
        else:
            facility_index += 1
            assert capacity_remaining[facility_index] >= customer.demand
            solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand

    used = [0]*len(facilities)
    for facility_index in solution:
        used[facility_index] = 1
    return (used, solution)

def load_input_data(file_location):
    input_data_file = open(file_location, 'r')
    input_data = ''.join(input_data_file.readlines())
    input_data_file.close()
    return input_data

def parse_input_data(input_data):

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        point = Point(float(parts[1]), float(parts[2]))
        facility_dist = [(length(point, facilities[i].location), i) for i in range(len(facilities))]
        facility_dist.sort()
        cust = Customer(len(customers), int(parts[0]), point, facility_dist)
        customers.append(cust)

    d = [None] * facility_count
    return Data(facilities, customers, d)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    data = parse_input_data(input_data)

    #(used,solution) = solve_it_example(data.facilities, data.customers)
    (used,solution) = solve_it_bruteforce(data)
    # facilities, customers, d = data
    # calculate the cost of the solution
    obj = sum([f.setup_cost*used[f.index] for f in data.facilities])
    for customer in data.customers:
        obj += length(customer.location, data.facilities[solution[customer.index]].location)

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        print 'Solving:', file_location
        print solve_it(load_input_data(file_location))
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)'


p0 = '25 50 \n7500 58268 430582.903998 430582.903998 \n7500 58268 441967.566511 447095.077733 \n7500 58268 432905.871800 444706.599336 \n7500 58268 427142.671483 433986.863525 \n7500 58268 428333.083285 439147.783561 \n7500 58268 430307.998493 442044.334989 \n7500 58268 434319.760208 348947.990899 \n7500 58268 437312.884269 236298.791087 \n7500 58268 429898.891150 440158.789247 \n7500 58268 468580.203206 309704.537261 \n0 58268 427330.722028 438586.802905 \n7500 58268 424118.342226 407682.076185 \n7500 58268 384802.033706 14516.509560 \n7500 58268 426329.771259 418931.439518 \n7500 58268 481984.149045 368646.428732 \n7500 58268 432098.903302 394292.526943 \n7500 58268 438572.694477 450113.198552 \n7500 58268 436874.502971 448932.035513 \n7500 58268 431558.339438 444153.081356 \n7500 58268 425944.670705 428053.302347 \n7500 58268 427630.945127 408740.437421 \n7500 58268 394480.895391 110170.066274 \n7500 58268 384295.454825 0.000000 \n7500 58268 388328.901804 13931.450473 \n7500 58268 435685.130355 447103.687854 \n146 416189.973974 279924.793498 \n87 416200.962928 279953.351993 \n672 416235.375342 281420.913036 \n1337 416041.801381 287758.719716 \n31 416203.112456 279952.407299 \n559 416217.961112 280854.973380 \n2370 407844.877813 313480.956397 \n1089 415956.078122 284292.337751 \n33 416202.706826 279950.944713 \n32 416203.385487 279953.320311 \n5495 301852.601198 459101.879327 \n904 416145.372162 282477.950440 \n1466 415753.199890 287343.540750 \n143 416205.945564 280029.518347 \n615 416128.050052 280314.598578 \n564 416005.244245 279715.008320 \n226 416190.248294 280030.155212 \n3016 404930.246190 319656.101204 \n253 416177.919605 280052.145685 \n195 416179.770958 279903.129895 \n38 416203.263566 279955.326144 \n807 416104.798995 280678.966717 \n551 416173.828443 280804.702077 \n304 416215.303062 280274.727997 \n814 416051.672631 280906.816241 \n337 416208.796835 280331.587594 \n4368 250434.121120 187215.186265 \n577 416187.082652 280929.527847 \n482 416196.152806 280491.239857 \n495 416225.028739 280836.244976 \n231 416206.203653 280094.445899 \n322 416204.643497 280254.428039 \n685 416204.142469 281045.423457 \n12912 498348.622166 1042778.922491 \n325 416179.102073 280057.581514 \n366 416161.819666 280094.540903 \n3671 333744.356821 398310.433016 \n2213 414235.515804 300297.443467 \n705 415188.053917 276838.289088 \n328 416206.142378 280393.884218 \n1681 415716.236926 286746.974892 \n1117 415698.915544 281877.987819 \n275 416119.647107 279722.785725 \n500 416137.917099 280096.149318 \n2241 400036.118513 242474.851379 \n733 415078.765968 276755.173333 \n222 416124.787869 279743.799920 \n49 416201.847278 279947.509166 \n1464 416009.615280 289392.477399 \n222 416191.073327 280003.552376\n'
