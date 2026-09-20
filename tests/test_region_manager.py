# tests/test_region_manager.py
from dsa.region_manager import RegionManager

def test_region_manager():
    manager = RegionManager()

    # 1. Test Insert & Search
    manager.insert_reading("North India", 101, 35.5)
    result = manager.search_reading("North India", 101)
    assert result == 35.5, f"Expected 35.5, got {result}"
    print("✓ Insert and Search Test Passed")

    # 2. Test Range Query
    manager.insert_reading("North India", 102, 36.0)
    manager.insert_reading("North India", 105, 38.0)
    range_res = manager.range_query("North India", 100, 103)
    assert len(range_res) == 2, f"Expected 2 records, got {len(range_res)}"
    print("✓ Range Query Test Passed")

    # 3. Test Delete
    manager.delete_reading("North India", 101)
    assert manager.search_reading("North India", 101) is None
    print("✓ Delete Test Passed")

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_region_manager()