# dsa/region_manager.py
import csv
from dsa.avl_tree import AVLTree

REGIONS = [
    "North India",
    "South India",
    "East India",
    "West India",
    "Central India",
    "Northeast India",
    "Islands"
]

class RegionManager:
    def __init__(self):
        # Map each region to an array index 0 to 6
        self.region_to_index = {region: idx for idx, region in enumerate(REGIONS)}
        # Array[7] holding individual AVL Trees
        self.region_array = [AVLTree() for _ in range(7)]
        self.region_counts = [0] * len(REGIONS)

    def _get_index(self, region: str) -> int:
        if region not in self.region_to_index:
            raise ValueError(f"Invalid Region: '{region}'. Must be one of {REGIONS}")
        return self.region_to_index[region]

    def insert_reading(self, region: str, timestamp: int, temperature: float):
        idx = self._get_index(region)
        if self.region_array[idx].search(timestamp) is None:
            self.region_counts[idx] += 1
        return self.region_array[idx].insert(timestamp, temperature)

    def search_reading(self, region: str, timestamp: int):
        idx = self._get_index(region)
        record = self.region_array[idx].search(timestamp)
        return None if record is None else record.max_temp

    def range_query(self, region: str, start: int, end: int):
        idx = self._get_index(region)
        return [
            {"timestamp": record.timestamp, "temperature": record.max_temp}
            for record in self.region_array[idx].range_query(start, end)
        ]

    def delete_reading(self, region: str, timestamp: int):
        idx = self._get_index(region)
        deleted = self.region_array[idx].delete(timestamp)
        if deleted:
            self.region_counts[idx] -= 1
        return deleted

    def region_count(self, region: str) -> int:
        return self.region_counts[self._get_index(region)]

    def get_root(self, region: str):
        return self.region_array[self._get_index(region)].root

    def load_from_csv(self, file_path: str):
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                region = row['region']
                timestamp = int(row['timestamp'])
                temperature = float(row['temperature'])
                self.insert_reading(region, timestamp, temperature)
                