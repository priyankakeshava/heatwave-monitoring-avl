# Heatwave Monitoring — Streamlit UI (Person 3's part)

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

It opens with 12 sample readings already seeded into each of the 7 regions
so the dashboard, search, range query, and tree views aren't empty.

## What's in here

- `app.py` — the whole UI: Dashboard, Insert, Search, Range Query, Delete,
  Tree Visualization, and an "About the Design" complexity summary. No AVL
  logic lives here — every operation just calls a `RegionManager` method.
- `mock_region_manager.py` — a **temporary** stand-in for
  `dsa/region_manager.py`. It implements the exact interface the team agreed
  on (`insert_reading`, `search_reading`, `range_query`, `delete_reading`),
  backed by a real small AVL tree per region, so the demo and the tree
  visualization behave correctly even before Person 1 & 2 finish.

## Swapping in the real DSA modules

Once Person 1 (`dsa/avl_tree.py`, `dsa/temp_record.py`) and Person 2
(`dsa/region_manager.py`) are done:

1. Drop their `dsa/` folder next to `app.py`.
2. Make sure `dsa/region_manager.py` exposes a `RegionManager` class with
   the same method names used here.
3. That's it — `app.py`'s import already tries `from dsa.region_manager
   import RegionManager` first and only falls back to the mock if that
   import fails. No UI code needs to change.

If the real `RegionManager` doesn't have a `get_root(region)` method for
the Tree Visualization page, either add a thin one that returns the root
node for a region, or leave that page showing its fallback message.

## Note on `region_count`

The mock tracks per-region counts itself (`region_count`). If the real
`RegionManager` doesn't expose that, the Dashboard page will just show
`"?"` for the metric — everything else still works.
