import unittest
from dsa.avl_tree import AVLTree


class TestAVLTree(unittest.TestCase):

    def test_ll_rotation(self):
        tree = AVLTree()
        for key in ["30", "20", "10"]:
            tree.insert(key, 40)
        self.assertEqual(tree.root.timestamp, "20")
        self.assertTrue(tree.is_balanced())

    def test_rr_rotation(self):
        tree = AVLTree()
        for key in ["10", "20", "30"]:
            tree.insert(key, 40)
        self.assertEqual(tree.root.timestamp, "20")
        self.assertTrue(tree.is_balanced())

    def test_lr_rotation(self):
        tree = AVLTree()
        for key in ["30", "10", "20"]:
            tree.insert(key, 40)
        self.assertEqual(tree.root.timestamp, "20")
        self.assertTrue(tree.is_balanced())

    def test_rl_rotation(self):
        tree = AVLTree()
        for key in ["10", "30", "20"]:
            tree.insert(key, 40)
        self.assertEqual(tree.root.timestamp, "20")
        self.assertTrue(tree.is_balanced())

    def test_search(self):
        tree = AVLTree()
        tree.insert("2026-05-01 10:00", 40)
        tree.insert("2026-05-01 12:00", 42)
        self.assertEqual(tree.search("2026-05-01 12:00").max_temp, 42)
        self.assertIsNone(tree.search("2026-05-01 15:00"))

    def test_range_query(self):
        tree = AVLTree()
        for timestamp, temp in [
            ("2026-05-01 10:00", 40),
            ("2026-05-02 10:00", 42),
            ("2026-05-03 10:00", 44),
            ("2026-05-04 10:00", 41),
        ]:
            tree.insert(timestamp, temp)

        result = tree.range_query(
            "2026-05-02 00:00",
            "2026-05-04 23:59"
        )

        self.assertEqual(
            [record.timestamp for record in result],
            [
                "2026-05-02 10:00",
                "2026-05-03 10:00",
                "2026-05-04 10:00",
            ],
        )

    def test_delete(self):
        tree = AVLTree()
        for key in ["20", "10", "30", "25", "40"]:
            tree.insert(key, 40)

        self.assertTrue(tree.delete("30"))
        self.assertIsNone(tree.search("30"))
        self.assertTrue(tree.is_balanced())


if __name__ == "__main__":
    unittest.main()
