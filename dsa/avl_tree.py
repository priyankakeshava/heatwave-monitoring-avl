# dsa/avl_tree.py
# Temporary mock class so Member 2 and Member 3 can build without waiting on Member 1.

class AVLTree:
    def __init__(self):
        self.data = {}

    def insert(self, timestamp: int, temperature: float):
        self.data[timestamp] = temperature
        return True

    def search(self, timestamp: int):
        return self.data.get(timestamp, None)

    def range_query(self, start: int, end: int):
        return [(ts, temp) for ts, temp in self.data.items() if start <= ts <= end]

    def delete(self, timestamp: int):
        if timestamp in self.data:
            del self.data[timestamp]
            return True
        return False