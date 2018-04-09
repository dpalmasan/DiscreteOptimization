#!/usr/bin/python
# -*- coding: utf-8 -*-

import heapq

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

class Queue:
    """
    Queue implementation
    """
    def __init__(self, queue=[]):
        self.queue = queue

    def isEmpty(self):
        return len(self.queue) == 0

    def enqueue(self, e):
        self.queue.append(e)

    def dequeue(self):
        return self.queue.pop(0)

    def __len__(self):
        return len(self.queue)
