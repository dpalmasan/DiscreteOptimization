#!/usr/bin/python
# -*- coding: utf-8 -*-

from ConstraintProgramming import *
from utils import PriorityQueue
import time
from math import ceil

def clique_number(node_count, edges):
    neighborcount = {node : 0 for node in range(node_count)}
    for node1, node2 in edges:
        neighborcount[node1] += 1
        neighborcount[node2] += 1
    lower_bound = 0
    for x in xrange(node_count):
        lower_bound += float(1)/(node_count - neighborcount[x])
    return int(ceil(lower_bound))


class GraphColoringCP(object):
    def __init__(self, node_count, edge_count, edges, colors=4):
        """
        The problem to solve is the following:
            minimize max c_i, for i in 0...(node_count-1)

            subject to: c_i != c_j (<i,j> in edges)
        Problem variables, domains and constraints are defined for the
        Graph Coloring. Since constraints between variables are non directed,
        I am using a frozenset so that (A,B) <=> (B,A)
        """
        self.__variables            = {"X%d" % node : None for node in range(node_count)}
        self.__domains              = {"X%d" % node: range(colors) for node in range(node_count)}
        self.__arcs                 = []
        self.__constraints          = {}
        self.__unassigned_variables = ["X%d" % node for node in range(node_count)]
        self.__start_time           = time.clock()
        self.__node_count           = node_count
        self.__colors               = colors

        for node1, node2 in edges:
            arc = frozenset(("X%d" % node1, "X%d" % node2))
            self.__arcs.append(arc)
            self.__constraints[arc] = ["variable[\"%s\"] != variable[\"%s\"]" % ("X%d" % node1, "X%d" % node2)]

        # Here I try to break symmetries by assigning value 1 to the node with
        # the maximum degree count
        neighborcount = {node : 0 for node in range(node_count)}
        neighbors     = {node : set([]) for node in range(node_count)}
        for node1, node2 in edges:
            neighbors[node1].add(node2)
            neighbors[node2].add(node1)
            neighborcount[node1] += 1
            neighborcount[node2] += 1

        node_max_degrees = max(neighborcount, key=neighborcount.get)
        self.__domains["X%d" % node_max_degrees] = [0]

        # I assign two to the neighbor which has the highest degree count
        # neighbor_max_degrees = None
        # max_degrees = -1
        # for neighbor in neighbors[node_max_degrees]:
        #     if neighborcount[neighbor] > max_degrees:
        #         max_degrees = neighborcount[neighbor]
        #         neighbor_max_degrees = neighbor
        # if not neighbor_max_degrees is None:
        #     self.__domains["X%d" % neighbor_max_degrees] = [1]




    def arcs(self):
        """
        Returns the arcs, which are basically arcs between variables, for
        relating them by constraints.
        """
        return list(self.__arcs)

    def constraints(self, Xi, Xj):
        return self.__constraints[frozenset((Xi, Xj))]

    def neighbors(self, X, removable_neighbor=None):
        neighbors = []
        for arc in self.__arcs:
            X1, X2 = arc

            if X1 == X:
                if not removable_neighbor is None:
                    if removable_neighbor != X2:
                        neighbors.append(X2)
                else:
                    neighbors.append(X2)
            elif X2 == X:
                if not removable_neighbor is None:
                    if removable_neighbor != X1:
                        neighbors.append(X1)
                else:
                    neighbors.append(X1)
        return neighbors

    def domain(self, Xi):
        return self.__domains[Xi]

    def remove_from_domain(self, x, Xi):
        self.__domains[Xi].remove(x)

    def unassigned_variables(self):
        return list(self.__unassigned_variables)

    def assign_variable(self, X, value, remove=False):
        """
        Assign value to the variable X
        TODO: Should I remove variable from unassigned variables?
        """
        self.__variables[X] = value
        if remove:
            self.__unassigned_variables.remove(X)

    def check_consistency(self):
        """
        Returns True if all the constraints are satisfied, false otherwise
        """
        variable            = {}
        for X in self.__variables:
            if not self.__variables[X] is None:
                variable[X] = self.__variables[X]

        variables = variable.keys()
        for i in xrange(len(variables)):
            Xi = variables[i]
            for j in xrange(i + 1, len(variables)):
                Xj = variables[j]
                try:
                    consistent = True
                    for constraint in self.__constraints[frozenset((Xi, Xj))]:
                        consistent = consistent and eval(constraint)
                        if not consistent:
                            return False
                except KeyError:
                    pass
        return True

    def get_domains(self):
        """
        I used this for debugging.
        """
        return self.__domains

    def get_variables(self):
        return self.__variables

    def get_start_time(self):
        return self.__start_time

    def __str__(self):
        s = ""
        for node in xrange(self.__node_count):
            s += "(vertex %d, color %s) - NeighborColors: ( " % (node, str(self.__variables["X%d" % node]))
            for neighbor in self.neighbors("X%d" % node):
                s += "%s " % (str(self.__variables[neighbor]))
            s += ")\n"
        return s

class GraphColoringGreedy(object):
    def __init__(self, node_count, edge_count, edges):
        self.__node_count       = node_count
        self.__edge_count       = edge_count
        self.__edges            = edges
        self.__neighbors        = {x: set([]) for x in range(node_count)}
        self.__neighborcount    = {x: 0 for x in range(node_count)}

        for x, y in self.__edges:
            self.__neighbors[x].add(y)
            self.__neighbors[y].add(x)
            self.__neighborcount[x] += 1
            self.__neighborcount[y] += 1

        minpq = PriorityQueue()
        for x in xrange(node_count):
            minpq.push(x, self.__neighborcount[x])

        self.__ordered_by_neighborcount = []
        while not minpq.isEmpty():
            self.__ordered_by_neighborcount.append(minpq.pop())

        self.__ordered_by_neighborcount.reverse()

    def solve(self):
        j = self.__ordered_by_neighborcount[0]
        self.__solution = {x: None for x in range(self.__node_count)}
        self.__solution[j] = 0

        for i in xrange(1, self.__node_count):
            j = self.__ordered_by_neighborcount[i]
            possible_colorings = []
            for neighbor in self.__neighbors[j]:
                if self.__solution[neighbor] is not None:
                    possible_colorings.append(self.__solution[neighbor])

            if len(possible_colorings) == 0:
                self.__solution[j] = 0
            else:
                current_min = min(possible_colorings)
                if current_min == 0:
                    self.__solution[j] = max(possible_colorings) + 1
                else:
                    self.__solution[j] = current_min - 1
        return self.__solution

    def solve_welsh_powell(self):
        color = 0
        self.__solution = {x: None for x in range(self.__node_count)}
        non_colored_list = list(self.__ordered_by_neighborcount)
        while len(non_colored_list) != 0:
            first_node = non_colored_list.pop(0)
            self.__solution[first_node] = color
            for node in list(non_colored_list):
                coloreable = True
                for neighbor in self.__neighbors[node]:
                    if self.__solution[neighbor] == color:
                        coloreable = False
                if coloreable:
                    self.__solution[node] = color
                    non_colored_list.remove(node)
            color += 1

        return self.__solution

if __name__ == "__main__":
    print "========================="
    print "Testing CP Solver"
    print "========================="
    cp = GraphColoringCP(5, 6, [(0,1), (0,2), (0,3), (2, 3), (2, 4), (3, 4)], 3)
    AC3(cp)
    sol = backtracking_search(cp)
    solution = [sol["X%d" % i] for i in xrange(5)]
    print sol
    print len(set(solution))
    print solution
    print "========================="
    print "Testing Greedy Solver"
    print "========================="
    gc = GraphColoringGreedy(5, 6, [(0,1), (0,2), (0,3), (2, 3), (2, 4), (3, 4)])
    sol = gc.solve()
    print sol
    solution = [sol[i] for i in xrange(5)]
    print len(set(solution))
    print solution
    print "========================="
    print "Testing Welsh Powell"
    print "========================="
    gc = GraphColoringGreedy(5, 6, [(0,1), (0,2), (0,3), (2, 3), (2, 4), (3, 4)])
    sol = gc.solve_welsh_powell()
    print sol
    solution = [sol[i] for i in xrange(5)]
    print len(set(solution))
    print solution
    gc = GraphColoringGreedy(7, 9, [(0,1), (0,2), (1,2), (1,6), (2,3), (2,4), (3,5), (4,5), (4,6)])
    sol = gc.solve_welsh_powell()
    print sol
    solution = [sol[i] for i in xrange(7)]
    print len(set(solution))
    print solution
