import bisect

class PriorityQueue:

    def __init__(self, f):
        self.queue = []
        self.f = f

    def append(self, item ):
        bisect.insort(self.queue, (self.f(item), item))

    def __len__(self):
        return len(self.queue)

    def pop(self):
        return self.queue.pop(0)[1]

    def __contains__(self, item):
        return any(item == pair[1] for pair in self.queue)

    def __getitem__(self, key):
        for _, item in self.queue:
            if item == key:
                return item

    def __delitem__(self, key):
        for i, (value, item) in enumerate(self.queue):
            if item == key:
                self.queue.pop(i)




