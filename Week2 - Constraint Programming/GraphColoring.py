#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO: Implement a Branch and Bounding approach, since it seems the CP based
# approach is too slow. My bet would be doing Greedy + Branch and Bounding to
# at least find a solution that passes the assignment.

from ConstraintProgramming import *
from utils import PriorityQueue
import operator
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

    def solve_first_fit(self):
        self.__solution = {x: None for x in range(self.__node_count)}
        self.__solution[0] = 0

        for i in xrange(1, self.__node_count):
            non_possible_colorings = set([])
            for neighbor in self.__neighbors[i]:
                if self.__solution[neighbor] is not None:
                    non_possible_colorings.add(self.__solution[neighbor])

            color = 0
            while self.__solution[i] is None:
                if color not in non_possible_colorings:
                    self.__solution[i] = color
                color += 1

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

    def solve_large_degree_ordering(self):
        self.__solution = {x: None for x in range(self.__node_count)}
        non_colored_list = list(self.__ordered_by_neighborcount)
        while len(non_colored_list) != 0:
            node = non_colored_list.pop(0)

            non_possible_colorings = set([])
            for neighbor in self.__neighbors[node]:
                if self.__solution[neighbor] is not None:
                    non_possible_colorings.add(self.__solution[neighbor])

            color = 0
            while self.__solution[node] is None:
                if color not in non_possible_colorings:
                    self.__solution[node] = color
                color += 1

        return self.__solution

    def solve_incidence_degree_ordering(self):
        self.__solution = {x: None for x in range(self.__node_count)}
        selected_node = self.__ordered_by_neighborcount[0]
        self.__solution[selected_node] = 0
        uncolored_nodes = self.__node_count - 1

        while uncolored_nodes > 0:
            adjacent_colored_count = {}
            for node in self.__solution:
                if self.__solution[node] is None:
                    colored_neighbors = 0
                    for neighbor in self.__neighbors[node]:
                        if self.__solution[neighbor] is not None:
                            colored_neighbors += 1
                    adjacent_colored_count[node] = colored_neighbors
            maximum_color_count = max(adjacent_colored_count.values())
            maximum_color_count_set = set([])
            for node in adjacent_colored_count:
                if adjacent_colored_count[node] == maximum_color_count:
                    maximum_color_count_set.add(node)

            if len(maximum_color_count_set) == 1:
                selected_node = maximum_color_count_set.pop()
            else:
                maximum_degree = -1
                selected_node = None
                for node in maximum_color_count_set:
                    if self.__neighborcount[node] > maximum_degree:
                        maximum_degree = self.__neighborcount[node]
                        selected_node = node
            color = 0
            while self.__solution[selected_node] is None:
                coloreable = True
                for neighbor in self.__neighbors[selected_node]:
                    if self.__solution[neighbor] == color:
                        coloreable = False
                        break
                if coloreable:
                    self.__solution[selected_node] = color
                    uncolored_nodes -= 1
                color += 1

        return self.__solution

    def solve_DSATUR(self):

        # Initialization
        self.__solution = {x: None for x in range(self.__node_count)}

        # Selecting first node, the node with the maximum degree
        selected_node = self.__ordered_by_neighborcount[0]
        self.__solution[selected_node] = 0
        uncolored_nodes = self.__node_count - 1

        while uncolored_nodes > 0:
            # Calculate the number of adjacent vertices with different
            # colors for every uncolored vertex
            adjacent_different_color_count = {}
            for node in self.__solution:
                if self.__solution[node] is None:
                    colored_neighbors = set([])
                    for neighbor in self.__neighbors[node]:
                        if self.__solution[neighbor] is not None:
                            colored_neighbors.add(neighbor)
                    adjacent_different_color_count[node] = len(colored_neighbors)

            maximum_color_count = max(adjacent_different_color_count.values())
            maximum_color_count_set = set([])
            for node in adjacent_different_color_count:
                if adjacent_different_color_count[node] == maximum_color_count:
                    maximum_color_count_set.add(node)

            if len(maximum_color_count_set) == 1:
                selected_node = maximum_color_count_set.pop()
            else:
                maximum_degree = -1
                selected_node = None
                for node in maximum_color_count_set:
                    if self.__neighborcount[node] > maximum_degree:
                        maximum_degree = self.__neighborcount[node]
                        selected_node = node
            color = 0
            while self.__solution[selected_node] is None:
                coloreable = True
                for neighbor in self.__neighbors[selected_node]:
                    if self.__solution[neighbor] == color:
                        coloreable = False
                        break
                if coloreable:
                    self.__solution[selected_node] = color
                    uncolored_nodes -= 1
                color += 1
        return self.__solution


    def solve_RLF(self):

        # Initialization
        self.__solution = {x: None for x in range(self.__node_count)}

        # Selecting first node, the node with the maximum degree
        selected_node = self.__ordered_by_neighborcount[0]
        active_color = 0
        uncolored_nodes = self.__node_count
        while uncolored_nodes > 0:
            self.__solution[selected_node] = active_color
            uncolored_nodes = self.__node_count - 1

            # Adjacent vertices of selected vertex are added to U
            U = set([])
            for node in xrange(self.__node_count):
                if node != selected_node and selected_node in self.__neighbors[node] and self.__solution[node] is None:
                    U.add(node)

            # The vertices which are not adjacent to selected node are added to V
            V = set([])
            for node in xrange(self.__node_count):
                if selected_node not in self.__neighbors[node] and node != selected_node and self.__solution[node] is None:
                    V.add(node)

            # Counting vertices adjacent that are in U
            while len(V) != 0:
                adjacent_vertex_u = {}
                for v in V:
                    count = 0
                    for adjacent in self.__neighbors[v]:
                        if adjacent in U:
                            count += 1
                    adjacent_vertex_u[v] = count

                selected_node = max(adjacent_vertex_u.iteritems(), key=operator.itemgetter(1))[0]
                self.__solution[selected_node] = active_color
                uncolored_nodes -= 1
                if selected_node in V:
                    V.remove(selected_node)
                U.add(selected_node)
                for node in self.__neighbors[selected_node]:
                    if node in V:
                        V.remove(node)
                    U.add(node)

            active_color += 1
            uncolored_adjacent_vertices = {}
            for node in self.__solution:
                if self.__solution[node] is None:
                    count = 0
                    for neighbor in self.__neighbors[node]:
                        if self.__solution[neighbor] is None:
                            count += 1
                    uncolored_adjacent_vertices[node] = count

            if len(uncolored_adjacent_vertices) == 0:
                return self.__solution
            maximum_uncolored_count = max(uncolored_adjacent_vertices.values())
            maximum_uncolored_count_set = set([])
            for node in uncolored_adjacent_vertices:
                if uncolored_adjacent_vertices[node] == maximum_uncolored_count:
                    maximum_uncolored_count_set.add(node)

            if len(maximum_uncolored_count_set) == 1:
                selected_node = maximum_uncolored_count_set.pop()
            else:
                maximum_degree = -1
                selected_node = None
                for node in maximum_uncolored_count_set:
                    if self.__neighborcount[node] > maximum_degree:
                        maximum_degree = self.__neighborcount[node]
                        selected_node = node

        return self.__solution

if __name__ == "__main__":
    print "========================="
    print "Testing CP Solver"
    print "========================="
    cp = GraphColoringCP(7, 9, [(0,1), (0,2), (1,2), (1,6), (2,3), (2,4), (3,5), (4,5), (4,6)], 3)
    AC3(cp)
    sol = backtracking_search(cp)
    solution = [sol["X%d" % i] for i in xrange(7)]
    print sol
    print len(set(solution))
    print solution
    print "========================="
    print "Testing Greedy Solver"
    print "========================="
    gc = GraphColoringGreedy(7, 9, [(0,1), (0,2), (1,2), (1,6), (2,3), (2,4), (3,5), (4,5), (4,6)])
    sol = gc.solve_first_fit()
    print sol
    solution = [sol[i] for i in xrange(7)]
    print len(set(solution))
    print solution
    print "========================="
    print "Testing Welsh Powell"
    print "========================="
    gc = GraphColoringGreedy(7, 9, [(0,1), (0,2), (1,2), (1,6), (2,3), (2,4), (3,5), (4,5), (4,6)])
    sol = gc.solve_welsh_powell()
    print sol
    solution = [sol[i] for i in xrange(7)]
    print len(set(solution))
    print solution
    print "========================="
    print "Testing Large Degree"
    print "========================="
    gc = GraphColoringGreedy(7, 9, [(0,1), (0,2), (1,2), (1,6), (2,3), (2,4), (3,5), (4,5), (4,6)])
    sol = gc.solve_large_degree_ordering()
    print sol
    solution = [sol[i] for i in xrange(7)]
    print len(set(solution))
    print solution
    print "========================="
    print "Testing Degree Ordering"
    print "========================="
    gc = GraphColoringGreedy(7, 9, [(0,1), (0,2), (1,2), (1,6), (2,3), (2,4), (3,5), (4,5), (4,6)])
    sol = gc.solve_incidence_degree_ordering()
    print sol
    solution = [sol[i] for i in xrange(7)]
    print len(set(solution))
    print solution

    print "========================="
    print "Testing DSATUR"
    print "========================="
    gc = GraphColoringGreedy(7, 9, [(0,1), (0,2), (1,2), (1,6), (2,3), (2,4), (3,5), (4,5), (4,6)])
    sol = gc.solve_DSATUR()
    print sol
    solution = [sol[i] for i in xrange(7)]
    print len(set(solution))
    print solution

    print "========================="
    print "Testing RLF"
    print "========================="
    gc = GraphColoringGreedy(7, 9, [(0,1), (0,2), (1,2), (1,6), (2,3), (2,4), (3,5), (4,5), (4,6)])
    sol = gc.solve_RLF()
    print sol
    solution = [sol[i] for i in xrange(7)]
    print len(set(solution))
    print solution
