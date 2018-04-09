#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO: I could not get as efficient as my previous code (the one that I created
# for the artificial intelligence class). I think I could improve performance
# I will leave the above note as is, just to note that the performance issue was
# not due the eval command, but due to I was evaluating constraints separately,
# using binary constraints in the check_consistency method. I changed that to
# an AllDifferent constraint and the performance improved dramatically, since
# I pruned lot of the search space. This shows that the AllDifferent constraint
# is useful in these cases for pruning the search space.

from ConstraintProgramming import *

class Sudoku(object):
    def __init__(self, sudoku):
        """
        Problem variables, domains and constraints are defined for the
        Sudoku. Since constraints between variables are non directed, I am
        using a frozenset so that (A,B) <=> (B,A)
        """
        self.__variables = {}
        self.__domains              = {}
        self.__arcs                 = []
        self.__constraints          = {}
        self.__unassigned_variables = []
        self.__alldifferent         = []


        rows = "ABCDEFGHI"
        cols = "123456789"
        i = 0
        for row in rows:
            for col in cols:
                self.__variables[row + col] = None if sudoku[i] == "0" else int(sudoku[i])
                self.__domains[row + col]   = range(1, 10) if sudoku[i] == "0" else [int(sudoku[i])]
                if sudoku[i] == "0":
                    self.__unassigned_variables.append(row + col)
                i += 1

        for i in rows:
            tmp = []
            for j in cols:
                tmp.append(i + j)
                for k in cols:
                    if j != k:
                        arc = frozenset((i + j, i + k))
                        if arc not in self.__arcs:
                            self.__arcs.append(arc)
                            self.__constraints[arc] = ["variable[\"%s\"] != variable[\"%s\"]" % (i + j, i + k)]
            self.__alldifferent.append(tmp)


        for i in cols:
            tmp = []
            for j in rows:
                tmp.append(j + i)
                for k in rows:
                    if j != k:
                        arc = frozenset((j + i, k + i))
                        if arc not in self.__arcs:
                            self.__arcs.append(arc)
                            self.__constraints[arc] = ["variable[\"%s\"] != variable[\"%s\"]" % (j + i, k + i)]
            self.__alldifferent.append(tmp)

        for i in xrange(3):
            for j in xrange(3):
                tmp = [row + col for row in rows[i*3:i*3+3] for col in cols[j*3:j*3+3]]
                self.__alldifferent.append(tmp)
                for r in tmp:
                    for c in tmp:
                        if r != c:
                            arc = frozenset((r, c))
                            if arc not in self.__arcs:
                                self.__arcs.append(arc)
                                self.__constraints[arc] = ["variable[\"%s\"] != variable[\"%s\"]" % (r, c)]



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
        Returns True if all the constraints are satisfied, false otherwise. This
        was implemented using AllDifferent constraint.
        """
        for variables in self.__alldifferent:
            for i in xrange(len(variables)):
                X = variables[i]
                for j in xrange(i + 1, len(variables)):
                    Y = variables[j]
                    are_assigned = not self.__variables[X] is None and not self.__variables[Y] is None
                    if are_assigned and self.__variables[X] == self.__variables[Y]:
                        return False
        return True

    def get_domains(self):
        """
        I used this for debugging.
        """
        return self.__domains

    def __str__(self):
        """
        I used this for debugging. Basically it gives the sudoku a string
        format
        """
        s = ""
        line = "-------------------------------------\n"
        s += line
        for row in "ABCDEFGHI":
            s += "|"
            for col in "123456789":
                if not self.__variables[row + col] is None:
                    s += ("%3d" % self.__variables[row + col]) + "|"
                else:
                    s += ("%3s" % ' ') + "|"
            s += "\n" + line

        return s

if __name__ == "__main__":
    # This is the sudoku shown in lecture
    lecture_example  = "000102900"
    lecture_example += "000090301"
    lecture_example += "000008006"
    lecture_example += "000030000"
    lecture_example += "062000000"
    lecture_example += "079016000"
    lecture_example += "008060007"
    lecture_example += "004000190"
    lecture_example += "000004020"
    cp = Sudoku(lecture_example)
    print "Initial Sudoku"
    print cp
    AC3(cp)
    sol = backtracking_search(cp)
    for X in sol:
        cp.assign_variable(X, sol[X])
    print "Solved Sudoku"
    print cp
