from dsa.temp_record import TempRecord


class AVLTree:
    """Custom timestamp-keyed AVL tree for Person 1's DSA contribution."""

    def __init__(self):
        self.root = None

    def _get_height(self, node):
        return 0 if node is None else node.height

    def _update_height(self, node):
        if node is not None:
            node.height = 1 + max(
                self._get_height(node.left),
                self._get_height(node.right)
            )

    def _get_balance(self, node):
        if node is None:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_right(self, y):
        x = y.left
        middle = x.right
        x.right = y
        y.left = middle
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x):
        y = x.right
        middle = y.left
        y.left = x
        x.right = middle
        self._update_height(x)
        self._update_height(y)
        return y

    def insert(self, timestamp, max_temp):
        self.root = self._insert(self.root, timestamp, max_temp)
        return self.search(timestamp)

    def _insert(self, node, timestamp, max_temp):
        if node is None:
            return TempRecord(timestamp, max_temp)

        if timestamp < node.timestamp:
            node.left = self._insert(node.left, timestamp, max_temp)
        elif timestamp > node.timestamp:
            node.right = self._insert(node.right, timestamp, max_temp)
        else:
            node.max_temp = max_temp
            return node

        self._update_height(node)
        balance = self._get_balance(node)

        if balance > 1 and timestamp < node.left.timestamp:
            return self._rotate_right(node)

        if balance < -1 and timestamp > node.right.timestamp:
            return self._rotate_left(node)

        if balance > 1 and timestamp > node.left.timestamp:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        if balance < -1 and timestamp < node.right.timestamp:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, timestamp):
        current = self.root
        while current is not None:
            if timestamp == current.timestamp:
                return current
            if timestamp < current.timestamp:
                current = current.left
            else:
                current = current.right
        return None

    def range_query(self, start, end):
        if start > end:
            return []
        result = []
        self._range_query(self.root, start, end, result)
        return result

    def _range_query(self, node, start, end, result):
        if node is None:
            return

        if node.timestamp > start:
            self._range_query(node.left, start, end, result)

        if start <= node.timestamp <= end:
            result.append(node)

        if node.timestamp < end:
            self._range_query(node.right, start, end, result)

    def delete(self, timestamp):
        if self.search(timestamp) is None:
            return False
        self.root = self._delete(self.root, timestamp)
        return True

    def _delete(self, node, timestamp):
        if node is None:
            return None

        if timestamp < node.timestamp:
            node.left = self._delete(node.left, timestamp)
        elif timestamp > node.timestamp:
            node.right = self._delete(node.right, timestamp)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            successor = self._min_value_node(node.right)
            node.timestamp = successor.timestamp
            node.max_temp = successor.max_temp
            node.right = self._delete(node.right, successor.timestamp)

        self._update_height(node)
        balance = self._get_balance(node)

        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)

        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)

        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node)
        self._inorder(node.right, result)

    def is_balanced(self):
        return self._check_balance(self.root)[0]

    def _check_balance(self, node):
        if node is None:
            return True, 0

        left_ok, left_height = self._check_balance(node.left)
        right_ok, right_height = self._check_balance(node.right)

        expected_height = 1 + max(left_height, right_height)
        ok = (
            left_ok and right_ok
            and abs(left_height - right_height) <= 1
            and node.height == expected_height
        )

        return ok, expected_height

