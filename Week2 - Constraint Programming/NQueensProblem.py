#!/usr/bin/python
# -*- coding: utf-8 -*-

from ConstraintProgramming import *

class NQueensProblem(ConstraintProgrammingProblem):
    def __init__(self, queens=8):
        """
        Here, the problem variables such as domain and constraints should
        be defined.
        """
        if queens == 2 or queens == 3:
            raise ValueError("There is no solution for N = %d" % queens)

        self.R                      = queens
        self.__domains              = {"row%d" % var: range(1, self.R + 1) for var in xrange(1, self.R + 1)}
        self.__arcs                 = []
        self.__constraints          = {}
        self.__variables            = {"row%d" % var: None for var in xrange(1, self.R + 1)}
        self.__unassigned_variables = ["row%d" % var for var in xrange(1, self.R + 1)]
        self.__variables_ordered    = ["row%d" % var for var in xrange(1, self.R + 1)]

        # Constraints
        for i in xrange(1, self.R + 1):
            for j in xrange(i+1, self.R + 1):
                arc = ("row%d" % i, "row%d" % j)
                self.__arcs.append(arc)
                self.__constraints[arc] = []
                self.__constraints[arc].append("variable[\"row%d\"] != variable[\"row%d\"]" % (i, j))
                self.__constraints[arc].append("variable[\"row%d\"] != variable[\"row%d\"] + %d" % (i, j, j - i))
                self.__constraints[arc].append("variable[\"row%d\"] != variable[\"row%d\"] - %d" % (i, j, j - i))

    def arcs(self):
        return list(self.__arcs)

    def constraints(self, Xi, Xj):
        return self.__constraints[(Xi, Xj)]

    def neighbors(self, X, removable_neighbor=None):
        neighbors = []
        for arc in self.__arcs:
            if X == arc[0]:
                if not removable_neighbor is None:
                    if removable_neighbor != arc[1]:
                        neighbors.append(arc[1])
                else:
                    neighbors.append(arc[1])
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
        variable_ordered    = []
        for X in self.__variables_ordered:
            if not self.__variables[X] is None:
                variable[X] = self.__variables[X]
                variable_ordered.append(X)
        if len(variable_ordered) == 0 or len(variable_ordered) == 1:
            return True

        consitent = True
        for i in xrange(len(variable_ordered)):
            Xi = variable_ordered[i]
            for j in xrange(i + 1, len(variable_ordered)):
                Xj = variable_ordered[j]
                consistent = True
                for constraint in self.__constraints[(Xi, Xj)]:
                    consistent = consistent and eval(constraint)
                    if not consistent:
                        return False
        return True

    def __str__(self):
        s = ""
        line = self.R*"----" + "-\n"
        s += line
        for m in xrange(1, self.R + 1):
            s += "|"
            for n in xrange(1, self.R + 1):
                if self.__variables["row%d" % m] == n:
                    s += ("%3s" % "Q") + "|"
                else:
                    s += ("%3s" % ' ') + "|"
            s += "\n" + line

        return s

if __name__ == '__main__':
    cp = NQueensProblem()

    # Testing arcs
    print cp.arcs()

    # Testing getting constraints
    print cp.constraints("row1", "row2")

    # Testing neighbors method
    print cp.neighbors("row1")

    # Testing neighbors removing "row2" if is it a neighbor
    print cp.neighbors("row1", "row2")

    # Testing domain method
    print cp.domain("row1")
    cp.remove_from_domain(1, "row1")
    print cp.domain("row1")

    # Testing check consistency with a solution
    cp.assign_variable("row1", 1)
    cp.assign_variable("row2", 5)
    cp.assign_variable("row3", 8)
    cp.assign_variable("row4", 6)
    cp.assign_variable("row5", 3)
    cp.assign_variable("row6", 7)
    cp.assign_variable("row7", 2)
    cp.assign_variable("row8", 4)
    print cp.check_consistency()

    # Testing check consistency with not a solution
    cp.assign_variable("row1", 1)
    cp.assign_variable("row2", 4)
    cp.assign_variable("row3", 2)
    cp.assign_variable("row4", 5)
    cp.assign_variable("row5", 8)
    cp.assign_variable("row6", 8)
    cp.assign_variable("row7", 5)
    cp.assign_variable("row8", 6)
    print cp.check_consistency()

    # Solving an instance with N = 16
    cp = NQueensProblem(16)
    sol = backtracking_search(cp)
    print sol
    for X in sol:
        cp.assign_variable(X, sol[X])
    print cp.check_consistency()
    print cp
