class TempRecord:
    def __init__(self, timestamp, max_temp):
        self.timestamp = timestamp
        self.max_temp = max_temp
        self.height = 1
        self.left = None
        self.right = None

    def __repr__(self):
        return f"TempRecord(timestamp={self.timestamp!r}, max_temp={self.max_temp!r})"
