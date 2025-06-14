class PriorityQueue():
    def __init__(self):
        self.Queue = []
    
    def Add(self, Priority, Item):
        self.Queue.append((Priority, Item))
        self.bubbleSort()
    
    def get(self):
        return self.Queue.pop()
    
    def isEmpty(self):
        return len(self.Queue) == 0
    
    def bubbleSort(self):
        n = len(self.Queue)
        
        for i in range(n):
            swapped = False    
            for j in range(0, n-i-1):
                if self.Queue[j] < self.Queue[j+1]:
                    self.Queue[j], self.Queue[j+1] = self.Queue[j+1], self.Queue[j]
                    swapped = True
            if (swapped == False):
                break