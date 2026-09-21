"""
mock_region_manager.py
-----------------------
TEMPORARY stand-in for dsa/region_manager.py.

This exists so Person 3 (Streamlit/UI) can build and test the whole app
before Person 1 (AVL) and Person 2 (RegionManager) finish their modules,
per the team's "no waiting chain" plan.

It implements the EXACT agreed interface:
    insert_reading(region, timestamp, temperature)
    search_reading(region, timestamp)
    range_query(region, start, end)
    delete_reading(region, timestamp)

so that app.py never needs to change when the real dsa.region_manager
is dropped in later -- only the import line at the top of app.py changes.

Internally it uses a real (if simplified) AVL tree per region, so the
tree visualization and complexity behavior look correct in the demo.
"""

import random
import datetime

REGIONS = [
    "Northwest", "Central", "East", "Northeast",
    "West", "South Peninsula", "Islands",
]


class AVLNode:
    __slots__ = ("timestamp", "temp", "height", "left", "right")

    def __init__(self, timestamp, temp):
        self.timestamp = timestamp
        self.temp = temp
        self.height = 1
        self.left = None
        self.right = None


def _h(node):
    return node.height if node else 0


def _update_height(node):
    node.height = 1 + max(_h(node.left), _h(node.right))


def _balance_factor(node):
    return _h(node.left) - _h(node.right) if node else 0


def _rotate_right(y):
    x = y.left
    t2 = x.right
    x.right = y
    y.left = t2
    _update_height(y)
    _update_height(x)
    return x


def _rotate_left(x):
    y = x.right
    t2 = y.left
    y.left = x
    x.right = t2
    _update_height(x)
    _update_height(y)
    return y


def _rebalance(node):
    _update_height(node)
    bf = _balance_factor(node)
    if bf > 1:
        if _balance_factor(node.left) < 0:
            node.left = _rotate_left(node.left)
        return _rotate_right(node)
    if bf < -1:
        if _balance_factor(node.right) > 0:
            node.right = _rotate_right(node.right)
        return _rotate_left(node)
    return node


def _insert(node, ts, temp):
    if node is None:
        return AVLNode(ts, temp)
    if ts < node.timestamp:
        node.left = _insert(node.left, ts, temp)
    elif ts > node.timestamp:
        node.right = _insert(node.right, ts, temp)
    else:
        node.temp = temp
        return node
    return _rebalance(node)


def _search(node, ts):
    if node is None or node.timestamp == ts:
        return node
    if ts < node.timestamp:
        return _search(node.left, ts)
    return _search(node.right, ts)


def _range_query(node, t1, t2, result):
    if node is None:
        return
    if node.timestamp > t1:
        _range_query(node.left, t1, t2, result)
    if t1 <= node.timestamp <= t2:
        result.append((node.timestamp, node.temp))
    if node.timestamp < t2:
        _range_query(node.right, t1, t2, result)


def _min_node(node):
    while node.left:
        node = node.left
    return node


def _delete(node, ts):
    if node is None:
        return None
    if ts < node.timestamp:
        node.left = _delete(node.left, ts)
    elif ts > node.timestamp:
        node.right = _delete(node.right, ts)
    else:
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        succ = _min_node(node.right)
        node.timestamp, node.temp = succ.timestamp, succ.temp
        node.right = _delete(node.right, succ.timestamp)
        return _rebalance(node)
    return _rebalance(node)


class MockRegionManager:
    """
    Drop-in stand-in for the real RegionManager. Same method names,
    same parameters, same return shapes -- so app.py doesn't care
    which one it's talking to.
    """

    def __init__(self):
        self.roots = {r: None for r in REGIONS}
        self.counts = {r: 0 for r in REGIONS}

    def insert_reading(self, region, timestamp, temperature):
        existed = _search(self.roots[region], timestamp) is not None
        self.roots[region] = _insert(self.roots[region], timestamp, temperature)
        if not existed:
            self.counts[region] += 1

    def search_reading(self, region, timestamp):
        node = _search(self.roots[region], timestamp)
        if node is None:
            return None
        return {"timestamp": node.timestamp, "temperature": node.temp}

    def range_query(self, region, start, end):
        result = []
        _range_query(self.roots[region], start, end, result)
        return [{"timestamp": ts, "temperature": t} for ts, t in result]

    def delete_reading(self, region, timestamp):
        existed = _search(self.roots[region], timestamp) is not None
        self.roots[region] = _delete(self.roots[region], timestamp)
        if existed:
            self.counts[region] -= 1
        return existed

    def region_count(self, region):
        return self.counts[region]

    def get_root(self, region):
        return self.roots[region]

    def seed_sample_data(self, n_per_region=12, seed=42):
        """Fill every region with a few sample readings so the demo
        isn't empty on first load."""
        rng = random.Random(seed)
        base = datetime.date(2024, 1, 1)
        for region in REGIONS:
            for _ in range(n_per_region):
                offset_days = rng.randint(0, 250)
                ts = (base + datetime.timedelta(days=offset_days)).strftime("%Y-%m-%d")
                temp = round(rng.uniform(24.0, 47.0), 1)
                self.insert_reading(region, ts, temp)
