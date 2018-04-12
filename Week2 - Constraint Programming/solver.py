#!/usr/bin/python
# -*- coding: utf-8 -*-
from GraphColoring import *

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


    #----------------------------------------------------------
    # FIXME: Add real solution (This is what I modified)
    gc = GraphColoringGreedy(node_count, edge_count, edges)
    sol = gc.solve_first_fit()
    solution = [sol[i] for i in xrange(node_count)]
    obj = len(set(solution))

    sol = gc.solve_welsh_powell()
    solution_tmp = [sol[i] for i in xrange(node_count)]
    if len(set(solution_tmp)) < obj:
        obj = len(set(solution_tmp))
        solution = solution_tmp

    sol = gc.solve_large_degree_ordering()
    solution_tmp = [sol[i] for i in xrange(node_count)]
    if len(set(solution_tmp)) < obj:
        obj = len(set(solution_tmp))
        solution = solution_tmp

    sol = gc.solve_incidence_degree_ordering()
    solution_tmp = [sol[i] for i in xrange(node_count)]
    if len(set(solution_tmp)) < obj:
        obj = len(set(solution_tmp))
        solution = solution_tmp

    sol = gc.solve_DSATUR()
    solution_tmp = [sol[i] for i in xrange(node_count)]
    if len(set(solution_tmp)) < obj:
        obj = len(set(solution_tmp))
        solution = solution_tmp

    sol = gc.solve_RLF()
    solution_tmp = [sol[i] for i in xrange(node_count)]
    if len(set(solution_tmp)) < obj:
        obj = len(set(solution_tmp))
        solution = solution_tmp

    # After this line I didn't modified anything
    #----------------------------------------------------------

    # build a trivial solution
    # every node has its own color
    #solution = range(0, node_count)

    # prepare the solution in the specified output format
    # output_data = str(node_count) + ' ' + str(0) + '\n'
    output_data = str(obj) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')
