#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
from operator import attrgetter
import heapq

# Problem sizes less than this constant, will be addressed by DP
MAX_ALLOWED_MEMORY = 20000000

class Stack:
    """
    Stack implementation, used for Depth First Branch and Bound
    """
    def __init__(self):
        self.stack = []

    def isEmpty(self):
        return len(self.stack) == 0

    def push(self, e):
        self.stack.insert(0, e)

    def pop(self):
        return self.stack.pop(0)

    def __len__(self):
        return len(self.stack)

class PriorityQueue:
    """
    Implements a priority queue data structure. Each inserted item
    has a priority associated with it and the client is usually interested
    in quick retrieval of the lowest-priority item in the queue. This
    data structure allows O(1) access to the lowest-priority item.

    Note that this PriorityQueue does not allow you to change the priority
    of an item.  However, you may insert the same item multiple times with
    different priorities.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0


class KnapsackNode(object):
    def __init__(self, value, room, estimate, parent=None, depth=0, index=None, assigned=0):
        self.value = value
        self.room = room
        self.estimate = estimate
        self.parent = parent
        self.assigned = assigned
        self.depth = depth
        self.index = index

    def expand(self, value, item_weight, new_estimate, index):
        left_node = KnapsackNode(self.value + value, self.room - item_weight, self.estimate, self, self.depth+1, index, 1)
        right_node = KnapsackNode(self.value, self.room, new_estimate, self, self.depth+1, index, 0)

        return [left_node, right_node]

    def __gt__(self, other):
        return self.estimate > other.estimate

    def __str__(self):
        return "value: %d, room: %d, estimate: %.2f, item_id: %d, assigned: %d" % (
            self.value, self.room, self.estimate, self.item_id, self.assigned)


def optimistic_estimate(items, capacity, current_weight=0, current_value=0):
    weight = current_weight
    value = current_value
    capacity_exceded = False
    for item in items:
        if weight + item.weight <= capacity:
            value += item.value
            weight += item.weight
        else:
            capacity_exceded = True
            break
    if weight < capacity and capacity_exceded:
        weight_fill = capacity - weight
        value += item.value * float(weight_fill)/item.weight

    return value

class Knapsack(object):
    def __init__(self, items, item_count, capacity):
        self.items      = list(items)
        self.item_count = item_count
        self.capacity   = capacity

    def trivial_greedy(self):
        """
        This is the approach that was in the initial code.
        Just put items in the knapsack as is, and fill it until
        it is full capacity.
        """
        value = 0
        weight = 0
        taken = [0]*len(self.items)

        for item in self.items:
            if weight + item.weight <= self.capacity:
                taken[item.index] = 1
                value += item.value
                weight += item.weight

        return (taken, value)

    def greedy_more_items(self):
        """
        This approach, uses the first greedy idea from the lecture. Takes
        as many items as possible, by sorting them by weight.
        """
        value = 0
        weight = 0
        taken = [0]*len(self.items)
        for item in sorted(self.items, key=attrgetter('weight')):
            if weight + item.weight <= self.capacity:
                taken[item.index] = 1
                value += item.value
                weight += item.weight
        return (taken, value)

    def greedy_most_valuable(self):
        """
        This approach, uses the second greedy idea from the lecture. Prefers
        taking most valuable items first.
        """
        value = 0
        weight = 0
        taken = [0]*len(self.items)
        for item in sorted(self.items, key=attrgetter('value'), reverse=True):
            if weight + item.weight <= self.capacity:
                taken[item.index] = 1
                value += item.value
                weight += item.weight
        return (taken, value)

    def greedy_density(self):
        """
        This approach, uses the second greedy idea from the lecture. Prefers
        taking most valuable items first.
        """
        Item = namedtuple("Item", ['index', 'density', 'weight', 'value'])
        items = []
        for item in self.items:
            items.append(
                Item(
                    item.index,
                    item.value/float(item.weight), item.weight, item.value
                )
            )

        value = 0
        weight = 0
        taken = [0]*len(items)
        for item in sorted(items, key=attrgetter('density'), reverse=True):
            if weight + item.weight <= self.capacity:
                taken[item.index] = 1
                value += item.value
                weight += item.weight
        return (taken, value)

    def dynamic_programming(self):
        """
        This implements the dynamic programming approach. Basically implements
        the recursive (divide and conquer) algorithm, using a table for avoiding
        doing re-computations.
        """
        dp_table = [
            [0 for j in xrange(self.item_count + 1)]
            for k in xrange(self.capacity + 1)
        ]

        for j in xrange(self.item_count + 1):
            for k in xrange(self.capacity + 1):
                if j == 0:
                    continue
                if self.items[j-1].weight <= k:
                    dp_table[k][j] = max(
                        dp_table[k][j - 1],
                        self.items[j-1].value + dp_table[k - self.items[j-1].weight][j - 1]
                    )
                else:
                    dp_table[k][j] = dp_table[k][j - 1]

        value = dp_table[self.capacity][self.item_count]
        taken = [0]*len(self.items)
        k = self.capacity
        for j in xrange(self.item_count, 0, -1):
            if dp_table[k][j] != dp_table[k][j-1]:
                taken[j-1] = 1
                traceback_value = dp_table[k][j] - self.items[j-1].value
                while traceback_value != dp_table[k][j-1] and k > 0:
                    k -= 1
        return (taken, value)

    def depth_first_branch_bound(self):
        """
        This implements depth-first branch and bound, using the optimistic estimate
        with relaxation (as the lecture). I should try improving this function by
        allowing specifying the estimate I want to use. For now, I am using the
        relaxation of allowing xi to be a real number
        """
        # Relaxation and optimal estimation
        Item = namedtuple("Item", ['index', 'density', 'weight', 'value'])
        items = []
        for item in self.items:
            items.append(
                Item(
                    item.index,
                    item.value/float(item.weight),
                    item.weight,
                    item.value
                )
            )
        items = sorted(items, key=attrgetter('density'), reverse=True)

        stack = Stack()
        root = KnapsackNode(0, self.capacity, optimistic_estimate(items, self.capacity))
        stack.push(root)
        best_solution_value = 0
        solution_node = None
        #n = 0
        while not stack.isEmpty():
            node = stack.pop()
            #n += 1
            # Prunning the search tree if I found a non good estimate
            #if node.item_id != self.item_count - 1:
                #if solution_node is not None and node.estimate < best_solution_value:
                #    continue
            #print node, best_solution_value
            #raw_input()
            if node.depth == self.item_count:
                if node.value > best_solution_value:
                    best_solution_value = node.value
                    solution_node = node

            elif node.estimate > best_solution_value:
                item = items[node.depth]
                neighbors = node.expand(
                    item.value,
                    item.weight,
                    optimistic_estimate(items[node.depth+1:], self.capacity, self.capacity - node.room, node.value),
                    items[node.depth].index
                )
                for neighbor in reversed(neighbors):
                    if neighbor.room >= 0 and neighbor.estimate > best_solution_value:
                        stack.push(neighbor)
                        #if neighbor.assigned == 1 and neighbor.value > best_solution_value:
                        #    best_solution_value = neighbor.value
            #else:
            #    if node.value > best_solution_value:
            #        best_solution_value = node.estimate
            #        solution_node = node
        #print "nodes expanded: ", n
        value = solution_node.value
        taken = [0]*len(self.items)
        while solution_node.parent is not None:
            taken[solution_node.index] = solution_node.assigned
            solution_node = solution_node.parent
        return (taken, value)

    def best_first_branch_bound(self):
        """
        This implements best-first branch and bound, using the optimistic estimate
        with relaxation (as the lecture). I should try improving this function by
        allowing specifying the estimate I want to use. For now, I am using the
        relaxation of allowing xi to be a real number
        """
        # Relaxation and optimal estimation
        Item = namedtuple("Item", ['index', 'density', 'weight', 'value'])
        items = []
        for item in self.items:
            items.append(
                Item(
                    item.index,
                    item.value/float(item.weight),
                    item.weight,
                    item.value
                )
            )
        items = sorted(items, key=attrgetter('density'), reverse=True)

        pq = PriorityQueue()
        root = KnapsackNode(0, self.capacity, optimistic_estimate(items, self.capacity))
        pq.push(root, root.estimate)
        best_solution_value = 0
        solution_node = None
        while not pq.isEmpty():
            node = pq.pop()
            if node.depth == self.item_count:
                if node.value > best_solution_value:
                    best_solution_value = node.value
                    solution_node = node

            elif node.estimate > best_solution_value:
                item = items[node.depth]
                neighbors = node.expand(
                    item.value,
                    item.weight,
                    optimistic_estimate(items[node.depth+1:], self.capacity, self.capacity - node.room, node.value),
                    items[node.depth].index
                )
                for neighbor in reversed(neighbors):
                    if neighbor.room >= 0 and neighbor.estimate > best_solution_value:
                        pq.push(neighbor, neighbor.estimate)

        value = solution_node.value
        taken = [0]*len(self.items)
        while solution_node.parent is not None:
            taken[solution_node.index] = solution_node.assigned
            solution_node = solution_node.parent
        return (taken, value)


    def hybrid_solver(self):
        """
        This solver is a hybrid one. For now it checks whether the problem
        is solvable by DP (by not using DP when the size is too big), and if
        not, just tries a greedy approach.
        """
        if self.capacity*self.item_count <= MAX_ALLOWED_MEMORY:
            #return self.dynamic_programming()
            return self.depth_first_branch_bound()
            #return self.greedy_density()
            #return self.best_first_branch_bound()
        else:
            #return self.dynamic_programming()
            return self.depth_first_branch_bound()
            #return self.greedy_density()
            #return self.best_first_branch_bound()

# Unit testing
if __name__ == "__main__":
    Item = namedtuple("Item", ['index', 'value', 'weight'])

    # Example 1 of dp slide
    item_count = 3
    capacity = 9
    items = [Item(0, 5, 4), Item(1, 6, 5), Item(2, 3, 2)]

    knapsack = Knapsack(items, item_count, capacity)

    print "Example 1:"
    print knapsack.trivial_greedy()
    print knapsack.greedy_more_items()
    print knapsack.greedy_most_valuable()
    print knapsack.greedy_density()
    print knapsack.dynamic_programming()
    print knapsack.depth_first_branch_bound()
    print knapsack.best_first_branch_bound()


    # Example 2
    item_count = 4
    capacity = 7
    items = [Item(0, 16, 2), Item(1, 19, 3), Item(2, 23, 4), Item(3, 28, 5)]
    knapsack = Knapsack(items, item_count, capacity)
    print "Example 2:"
    print knapsack.trivial_greedy()
    print knapsack.greedy_more_items()
    print knapsack.greedy_most_valuable()
    print knapsack.greedy_density()
    print knapsack.dynamic_programming()
    print knapsack.depth_first_branch_bound()
    print knapsack.best_first_branch_bound()

    # This is the first lecture example
    item_count = 7
    capacity = 10
    items = [Item(0, 10, 5), Item(1, 1, 2), Item(2, 1, 2),
        Item(3, 10, 5), Item(4, 1, 2), Item(5, 13, 8),
        Item(6, 7, 3)]
    knapsack = Knapsack(items, item_count, capacity)
    print "Example Indiana Jones:"
    print knapsack.trivial_greedy()
    print knapsack.greedy_more_items()
    print knapsack.greedy_most_valuable()
    print knapsack.greedy_density()
    print knapsack.dynamic_programming()
    print knapsack.depth_first_branch_bound()
    print knapsack.best_first_branch_bound()

    item_count = 3
    capacity = 10
    items = [Item(0, 45, 5), Item(1, 48, 8), Item(2, 35, 3)]
    knapsack = Knapsack(items, item_count, capacity)
    print "Example Search and Bound:"
    print knapsack.trivial_greedy()
    print knapsack.greedy_more_items()
    print knapsack.greedy_most_valuable()
    print knapsack.greedy_density()
    print knapsack.dynamic_programming()
    print knapsack.depth_first_branch_bound()
    print knapsack.best_first_branch_bound()
