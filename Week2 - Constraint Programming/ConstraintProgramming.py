#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO: Come up with a better solution for representing constraints, since
# using eval is bad practice and also is slow, which I proved when testing
# the Sudoku implementation. I think, the best idea would be just using the
# AllDifferent constraint for problem's constraints.

from abc import ABCMeta, abstractmethod
from utils import Queue, PriorityQueue
from copy import deepcopy
import time

MAX_TIME_ALLOWANCE = 60

class ConstraintProgrammingProblem(object):
    """
    This is the Base Class for the Constraining Programming framework I am
    writing for this class. There are lots of improvements I'd like to make:
        - I don't think any of the methods should be abstract, except the
        check_consistency method. Which perhaps I did not design correctly.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def arcs(self):
        """
        This method should return a list of arcs between variables.
        """
        pass

    @abstractmethod
    def constraints(self, Xi, Xj):
        """
        This method returns all the constraints between variables Xi and Xj
        """
        pass

    @abstractmethod
    def neighbors(self, Xi, removable_neighbor):
        """
        This method returns all neighbors of Xi (based on arcs), if removable
        neighbor is different of None, the returned list of neighbors will not
        contain the removable_neighbor
        """
        pass

    @abstractmethod
    def domain(self, Xi):
        """
        Returns a list, which are the values for variable Xi
        """
        pass

    @abstractmethod
    def remove_from_domain(self, x, Xi):
        """
        Removes value x from the domain of variable Xi
        """
        pass

    @abstractmethod
    def unassigned_variables(self):
        """
        Returns a list of all unassigned variables.
        """
        pass

    @abstractmethod
    def assign_variable(self, X, value, remove):
        """
        Assign a value to the variable X. If remove is set to True, the variable
        X is removed from the unassigned variables list.
        """
        pass

    @abstractmethod
    def check_consistency(self):
        """
        Checks consistency of the current assignment.
        """
        pass

def AC3(csp):
    """
    Returns False if an inconsistency is found, True otherwise
    Input: A CSP with components (X, D, C)
    """

    # Initially, the queue has all the arcs in the CSP
    queue = Queue(csp.arcs())

    while not queue.isEmpty():
        (Xi, Xj) = queue.dequeue()
        if revise(csp, Xi, Xj):
            if len(csp.domain(Xi)) == 0:
                return False
            for Xk in csp.neighbors(Xi, Xj):
                queue.enqueue((Xk, Xi))
    return True

def revise(csp, Xi, Xj):
    """
    Returns True iff we revise the domain of Xi
    """
    revised = False
    variable = {Xi: None, Xj: None}
    for x in csp.domain(Xi):
        variable[Xi] = x
        constraints_satisfied = False
        for y in csp.domain(Xj):
            variable[Xj] = y
            satisfied = True
            for constraint in csp.constraints(Xi, Xj):
                satisfied = satisfied and eval(constraint)
            constraints_satisfied = satisfied
            if constraints_satisfied:
                break
        if not constraints_satisfied:
            csp.remove_from_domain(x, Xi)
            revised = True
    return revised

def forward_checking(csp, var, value):
    """
    Given an assignment, uses forward checking to make inferences about possible
    assignments for free variables. Returns True if no variable domain is empty,
    and the inference maintains consistency, False otherwise
    """
    variables = csp.unassigned_variables()
    if var in variables:
        variables.remove(var)

    for X in variables:
        for val in csp.domain(X):
            csp.assign_variable(X, val)
            if not csp.check_consistency():
                csp.remove_from_domain(val, X)
            if len(csp.domain(X)) == 0:
                return False
        if len(csp.domain(X)) == 1:
            csp.assign_variable(X, csp.domain(X)[0])
        else:
            csp.assign_variable(X, None)
    if not csp.check_consistency():
        return False
    return True

def least_constraining_value(var, assignment, csp):
    """
    Implements Least Constraining Value Heuristic (LCV), which order the domain
    values in the order in which they rule out the fewest values in the remaining
    variables
    """
    variables = csp.unassigned_variables()
    variables.remove(var)
    for X in assignment:
        if X in variables:
            variables.remove(X)

    minpq = PriorityQueue()
    for val in csp.domain(var):
        csp.assign_variable(var, val)
        values_ruled_out = 0
        for X in variables:
            for v in csp.domain(X):
                csp.assign_variable(X, v)
                if not csp.check_consistency():
                    values_ruled_out += 1
                csp.assign_variable(X, None)
        csp.assign_variable(var, None)
        minpq.push(val, values_ruled_out)

    domain_ordered = []
    while not minpq.isEmpty():
        domain_ordered.append(minpq.pop())
    return domain_ordered

def backtracking_search(csp, time_limit=False, inference=forward_checking, order_domain_values=least_constraining_value):
    """
    Returns a solution or failure
    """
    return backtrack({}, csp, time_limit, inference, order_domain_values)

def backtrack(assignment, csp, time_limit, inference, order_domain_values):
    """
    Recursive method for finding the assignment of variables that satisfies
    all the constraints.
    """
    # Get unassigned variables
    variables = csp.unassigned_variables()
    for key in assignment.keys():
        if key in variables:
            variables.remove(key)

    # Assignment Complete
    if len(variables) == 0:
        return assignment

    # Pick the next variable to be assigned using MRV heuristic
    maxDi = float('Inf')
    var = None
    for X in variables:
        if len(csp.domain(X)) < maxDi:
            maxDi = len(csp.domain(X))
            var = X

    for value in order_domain_values(var, assignment, csp):
        cspTemp = deepcopy(csp)
        cspTemp.assign_variable(var, value, True)
        if cspTemp.check_consistency():
            assignment[var] = value
            inferences = []
            if inference(cspTemp, var, value):
                for v in cspTemp.unassigned_variables():
                    if len(cspTemp.domain(v)) == 1:
                        assignment[v] = cspTemp.domain(v)[0]
                        inferences.append(v)
            result = backtrack(assignment, cspTemp, time_limit, inference, order_domain_values)
            if result != False:
                return result

            # Remove var and inferences from assignment
            assignment.pop(var, None)
            for v in inferences:
                assignment.pop(v, None)

    return False
