# Heatwave Monitoring

A Streamlit application for monitoring temperature readings across seven Indian regions. Each region is backed by its own timestamp-keyed AVL tree.

## Run Locally

From the project directory:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually `http://localhost:8501`.

## Features

The sidebar provides these views:

- **Dashboard**: reading counts by region and a complete regional overview.
- **Insert Reading**: add or update a reading by region, date, and temperature.
- **Search Reading**: find all readings for a selected calendar date and region.
- **Range Query**: return readings between two dates, including readable UTC times.
- **Delete Reading**: delete all readings for a selected date and region.
- **Tree Visualization**: inspect the AVL tree for one region, including node count, height, root balance, and readable node timestamps.
- **All Data**: display the complete dataset with region, recorded UTC time, raw timestamp, and temperature.
- **About the Design**: review the data-structure choices and operation complexity.

The application also displays the current UTC clock separately from the recorded time of each weather reading.

## Data Storage

The default dataset is stored at:

```text
data/weather_data.csv
```

The CSV must contain these columns:

```csv
region,timestamp,temperature
North India,1700000000,32.5
```

`timestamp` is a Unix timestamp in seconds. The AVL tree uses this numeric value as its sorting key. The interface converts it to a readable UTC date and time when displaying results.

The bundled CSV is loaded when the app starts. Insertions and deletions update both the in-memory AVL tree and the local CSV file:

- A new `region + timestamp` pair is appended.
- An existing `region + timestamp` pair updates its temperature.
- Deleting a reading removes the matching CSV row.

## Pseudocode

### Load CSV

```text
create an empty AVL tree for each region
for each row in weather_data.csv:
	read region, timestamp, and temperature
	insert the reading into that region's AVL tree
```

### Insert Reading

```text
convert selected date to a Unix timestamp
find the AVL tree for the selected region
if timestamp already exists:
	update its temperature
else:
	insert a new node
rebalance the tree
write the new value to the CSV file
```

### Search Reading

```text
convert selected date to the start and end of that UTC day
find the selected region's AVL tree
run a range query between those timestamps
display every matching reading with readable date and time
```

### Range Query

```text
convert start date to a Unix timestamp
convert end date to the final second of that UTC day
find the selected region's AVL tree
return all nodes between the two timestamps in sorted order
```

### Delete Reading

```text
find all readings for the selected region and UTC day
for each matching reading:
	delete it from the AVL tree
	rebalance the tree
	remove it from the CSV file
```

### AVL Rebalancing

```text
balance factor = height(left subtree) - height(right subtree)
if balance factor is greater than 1:
	perform a right rotation or left-right rotation
if balance factor is less than -1:
	perform a left rotation or right-left rotation
update node heights
```

## Project Structure

```text
heatwave-monitoring-avl-main/
├── app.py                         Streamlit interface and CSV persistence
├── requirements.txt               Python dependencies
├── data/
│   └── weather_data.csv           Default readings
├── dsa/
│   ├── __init__.py
│   ├── avl_tree.py                AVL tree operations
│   ├── region_manager.py          Seven-region AVL tree manager
│   └── temp_record.py             AVL node model
└── tests/
	├── __init__.py
	├── test_avl.py                AVL tree tests
	└── test_region_manager.py     Region manager tests
```

## Tests

```bash
python -m unittest discover -v
python -m py_compile app.py dsa/avl_tree.py dsa/region_manager.py dsa/temp_record.py
```
