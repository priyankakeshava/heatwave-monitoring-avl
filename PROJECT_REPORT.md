# Heatwave Monitoring — Project and DSA Report

## 1. Project overview

Heatwave Monitoring is a Streamlit application for browsing temperature readings
from seven Indian regions. Its central data-structure design is an **array of
seven AVL trees**: each region has its own AVL tree, and Unix timestamps are
the keys inside that tree. The application can insert or update readings,
search by date, query a date range, delete readings for a day, display all
loaded data, and visualize a region's tree.

The design separates responsibilities:

```text
Streamlit interface and CSV persistence (app.py)
                    |
             RegionManager
                    |
       fixed region index + 7 AVL trees
                    |
    timestamp-keyed TempRecord nodes
```

## 2. Project files

| File | Responsibility |
| --- | --- |
| `app.py` | Builds the Streamlit pages, turns dates into UTC timestamps, calls the manager, renders tables/charts/tree diagrams, and saves changes to the CSV. It does not implement AVL rotations or tree operations. |
| `dsa/temp_record.py` | Defines one AVL node: timestamp key, temperature value, stored subtree height, and left/right child references. |
| `dsa/avl_tree.py` | Implements binary-search-tree insertion, lookup, range traversal, deletion, inorder traversal, rotations, height maintenance, and balance checking. |
| `dsa/region_manager.py` | Maps each of the seven supported region names to an index and routes operations to that region's AVL tree. It also tracks per-region reading counts and loads CSV rows. |
| `data/weather_data.csv` | Small sample dataset, with `region`, Unix-seconds `timestamp`, and `temperature` columns. |
| `tests/test_avl.py` | `unittest.TestCase` tests for all four insertion rotations, lookup, range query, and deletion. |
| `tests/test_region_manager.py` | A standalone integration-style test of manager insertion/search, range query, and deletion. |
| `requirements.txt` | Declares Streamlit and pandas as application dependencies. |
| `README.md` | Setup instructions, feature list, storage format, pseudocode, and a short architecture description. |

## 3. Data model and regional indexing

`REGIONS` is the canonical ordered list of seven supported region names.
`RegionManager` builds two parallel structures from it:

1. `region_to_index`, a dictionary mapping a region name to an integer from 0
   through 6.
2. `region_array`, a Python list containing one `AVLTree` at each corresponding
   index.

For example, a request for `"North India"` looks up its index and then operates
on that tree. The name-to-index lookup is average **O(1)**, as is indexing the
list. Using a separate tree per region keeps readings from different regions
independent even when they have the same timestamp. `_get_index` also rejects
unknown region names with a `ValueError`.

`region_counts` is another fixed-size list aligned to the same indices. The
manager increments a count only when an insertion adds a previously unseen
timestamp; replacing an existing timestamp's temperature does not increase the
count. A successful deletion decreases the count.

## 4. AVL tree concepts and implementation

### 4.1 Binary-search-tree ordering

Each `TempRecord` node is keyed by `timestamp`. For any node:

- timestamps in its left subtree are smaller;
- timestamps in its right subtree are larger;
- an equal timestamp updates that node's temperature rather than adding a
  duplicate key.

This gives the tree its binary-search property. The application uses integer
Unix timestamps in seconds. Some AVL unit tests use strings as keys; the tree
uses ordinary Python ordering comparisons and does not itself convert key types.
Callers should use one consistent, mutually comparable key type within a tree.

The timestamp is unique **within a region**, not globally. Thus the same
timestamp can appear once in each of several regional trees.

### 4.2 Node fields and subtree height

`TempRecord` stores:

- `timestamp`: the comparison/sort key;
- `max_temp`: the recorded temperature;
- `left` and `right`: references to child nodes;
- `height`: the height of the subtree rooted at that node.

An empty subtree has height 0; a new leaf has height 1. After a structural
change, `_update_height` recomputes a node's height as:

```text
1 + max(height(left), height(right))
```

Keeping heights on nodes makes balance-factor checks efficient: the algorithm
reads a child's stored height rather than recounting every descendant.

### 4.3 AVL balance and rotations

An AVL tree is a binary search tree that keeps the heights of the two child
subtrees of every node within one of each other. This implementation defines
the balance factor as:

```text
balance(node) = height(node.left) - height(node.right)
```

A node is locally AVL-balanced when its balance factor is `-1`, `0`, or `1`.
An insertion or deletion can make the factor `2` or `-2`; the tree then rotates
to restore balance while preserving timestamp ordering.

The four insertion cases covered by the implementation and tests are:

| Case | Shape of the new heavy path | Repair |
| --- | --- | --- |
| LL | left child, then its left subtree | One right rotation |
| RR | right child, then its right subtree | One left rotation |
| LR | left child, then its right subtree | Left rotation on the child, then right rotation |
| RL | right child, then its left subtree | Right rotation on the child, then left rotation |

`_rotate_left` and `_rotate_right` rewire the relevant parent/child links. Each
rotation updates the height of the node moved downward before updating the new
subtree root. This order ensures the second height calculation uses current
child heights.

Insertion recursively follows the BST ordering to the key's position, creates
a leaf or updates an equal key, updates ancestor heights, checks balance, and
applies the appropriate rotation. Because AVL height is logarithmic, a
single-key insertion remains **O(log n)**.

### 4.4 Lookup

`search` iteratively compares the target timestamp with the current node. It
returns the node on equality, moves left for a smaller key, and moves right for
a larger key. Reaching an empty child means the key is absent. Its complexity
is **O(log n)** in an AVL tree.

The manager's `search_reading` exposes only the temperature value (or `None`)
instead of exposing the node itself.

### 4.5 Range query and inorder traversal

`range_query(start, end)` returns nodes whose timestamps lie in the inclusive
interval `[start, end]`. If `start > end`, it returns an empty list.
`_range_query` recursively prunes branches that cannot contain a result:

- it visits the left side only when the current timestamp is greater than the
  lower bound;
- it appends the current node when `start <= timestamp <= end`;
- it visits the right side only when the current timestamp is less than the
  upper bound.

The traversal examines only relevant paths and matching records in the usual
balanced-tree range-query model: **O(log n + k)**, where `k` is the number of
returned readings. If most or all records match, output itself can require
**O(n)** time.

`inorder` visits left subtree, node, then right subtree. Since the tree is a
BST, this produces timestamps in ascending order. `RegionManager.all_readings`
uses this traversal for every region, so producing the complete dataset takes
**O(N)** time for `N` total records (plus the fixed seven-region iteration).

### 4.6 Deletion

Deletion first checks that the key exists; absent keys return `False`. The
recursive delete then handles the standard BST cases:

1. **No left child:** replace the node with its right child.
2. **No right child:** replace the node with its left child.
3. **Two children:** find the smallest node in the right subtree (the inorder
   successor), copy its timestamp and temperature into the target, then remove
   the successor from the right subtree.

On the way back up the recursion, the tree recalculates heights and rebalances.
Deletion uses the child's balance factor to choose the single or double
rotation. Its asymptotic cost is **O(log n)**.

### 4.7 Complexity summary

Here, `n` is the number of readings in the selected region and `k` is the
number of matching readings returned by a range query.

| Operation | Complexity | Reason |
| --- | --- | --- |
| Select a region | Average O(1) | Dictionary lookup and fixed-list indexing. |
| Read a regional count | O(1) | Direct access to `region_counts`. |
| Insert/update a reading | O(log n) | AVL descent and rebalancing; duplicate keys update their value. |
| Search one timestamp | O(log n) | AVL height bounds the search path. |
| Query a timestamp range | O(log n + k) | Pruned tree traversal plus output. |
| Delete one timestamp | O(log n) | BST deletion followed by AVL rebalancing. |
| List one tree in sorted order | O(n) | Inorder traversal visits each node once. |
| List all regions' readings | O(N) | Each of the `N` nodes is visited once. |
| Store the readings | O(N) | One node per distinct region/timestamp pair. |

The manager performs preliminary lookups around insertion and deletion, so an
operation may make more than one logarithmic traversal. This changes constant
factors, not the asymptotic complexity.

## 5. Application pages and end-to-end flow

The application loads `data/weather_data.csv` when `get_manager` creates the
cached manager. `@st.cache_resource` keeps that manager object available across
Streamlit reruns in the same app process. The main user-facing pages work as
follows:

- **Dashboard:** displays each region's reading count, a count chart, and the
  runtime architecture.
- **Insert Reading:** accepts a region, calendar date, and temperature. The
  selected date is converted to midnight UTC, stored as Unix seconds, written
  to CSV, and inserted into the in-memory AVL tree. An existing
  region/timestamp pair is replaced.
- **Search Reading:** turns a selected UTC date into the inclusive timestamp
  interval from midnight through 23:59:59 UTC and returns all readings in that
  interval.
- **Range Query:** applies the same conversion to a start and end date, rejects
  a start date later than the end date, and displays the sorted results.
- **Delete Reading:** queries the selected UTC day, then deletes each matching
  timestamp from both the regional AVL tree and the CSV.
- **Tree Visualization:** reports node count, root height, and root balance
  factor, then renders the tree as a Graphviz diagram. Nodes show readable UTC
  time, temperature, and their own balance factor.
- **All Data:** combines every region's inorder traversal and displays region,
  readable UTC time, raw timestamp, and temperature.
- **About the Design:** presents the selected structure and a short complexity
  table.

The current UTC clock shown in the page header is the app's clock. It is
separate from each record's timestamp, which represents when that reading
belongs.

### CSV update behavior

On insertion, the app reads the CSV, retains the expected columns, removes rows
whose timestamp cannot be parsed as numeric, appends the new value, keeps the
last row for a duplicate `(region, timestamp)`, sorts by region and timestamp,
and rewrites the CSV. Deletion filters out the matching region/timestamp and
rewrites the file. After an application restart, the CSV is the source from
which the in-memory trees are rebuilt.

The date picker in the insertion page selects one calendar date and the app
uses that date's midnight timestamp. Therefore, inserting twice for the same
region and date through that form updates the same key; data loaded from a CSV
can still contain several different timestamps on one day.

## 6. Sample data

The bundled CSV has six records: two for North India and one each for South,
East, West, and Central India. Northeast India and Islands start empty. The
timestamp is stored as an integer number of seconds since the Unix epoch; the
interface formats it as UTC for display.

## 7. Verification performed

- `python -m unittest discover -v` passed all **7 AVL tree tests**: LL, RR, LR,
  and RL insertion rotations, search, range query, and delete.
- The standalone manager checks passed when run as
  `python -m tests.test_region_manager` with UTF-8 output enabled. They exercise
  insert/search, range query, and delete through `RegionManager`.
- `python -m py_compile app.py dsa\avl_tree.py dsa\region_manager.py
  dsa\temp_record.py` completed successfully.
- The Streamlit server responded locally and was opened in a browser. The
  dashboard showed all seven expected region counts; the North India
  visualization rendered two nodes, height 2, and root balance -1.

The browser verification confirmed the dashboard and tree visualization.
Search and range operations are also covered at the DSA/manager layer by the
tests above; the date-picker interaction was not used as a browser-level test.

## 8. Notes and limitations

- The conventional `unittest discover` run does not execute
  `test_region_manager.py`'s plain function because it is not a `unittest`
  `TestCase` method. Run it separately as a module to exercise those checks.
- Running that manager test with a Windows console using the default
  `cp1252` output encoding may fail when it prints checkmark characters. Setting
  `PYTHONIOENCODING=utf-8` for the command allows the script to complete.
- The opening comment in `app.py` describes the old mock-manager fallback, but
  this repository contains and imports the real `dsa.region_manager` module.
  The report follows the active implementation.
- CSV persistence is local-file persistence, not a transactional database.
  The app does not implement concurrent-writer coordination or recovery from
  malformed CSV rows beyond the numeric-timestamp cleanup during save.
