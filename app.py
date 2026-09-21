"""
app.py — Streamlit presentation layer (Person 3's part)
--------------------------------------------------------
Rules followed from the team's design doc:
  - This file contains NO AVL logic. It only calls RegionManager methods.
  - It uses the mock RegionManager until the real dsa/ modules exist.
  - To connect the real DSA modules later: just make sure dsa/region_manager.py
    exists with a RegionManager class exposing the same methods, and the
    import below will pick it up automatically (no other code changes needed).
"""

import datetime
import pandas as pd
import streamlit as st

try:
    # This becomes active the moment Person 1 & 2 finish dsa/region_manager.py
    from dsa.region_manager import RegionManager  # noqa: F401
except ImportError:
    from mock_region_manager import MockRegionManager as RegionManager

REGIONS = [
    "Northwest", "Central", "East", "Northeast",
    "West", "South Peninsula", "Islands",
]

st.set_page_config(page_title="Heatwave Monitoring — Array[7] of AVL Trees", layout="wide")


@st.cache_resource
def get_manager():
    mgr = RegionManager()
    if hasattr(mgr, "seed_sample_data"):
        mgr.seed_sample_data()
    return mgr


manager = get_manager()

st.title("🌡️ Heatwave Monitoring System")
st.caption("Array[7] of AVL Trees, keyed by timestamp — DSA IA (Case Study KJS-CES-01)")

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to",
        [
            "Dashboard",
            "Insert Reading",
            "Search Reading",
            "Range Query",
            "Delete Reading",
            "Tree Visualization",
            "About the Design",
        ],
    )
    st.divider()
    st.caption("Person 3 — Streamlit / Visualization")
    st.caption("Presentation layer only. DSA logic lives in dsa/region_manager.py.")


def build_dot(node, graph_name):
    """Build a Graphviz DOT string for one region's AVL tree."""
    lines = [f"digraph {graph_name} {{", 'node [shape=circle, style=filled, fontsize=10, fixedsize=true, width=1.0];']
    if node is None:
        lines.append('empty [label="(empty)", shape=plaintext];')
    else:
        counter = [0]

        def h(n):
            return n.height if n else 0

        def rec(n):
            if n is None:
                return None
            my_id = f"n{counter[0]}"
            counter[0] += 1
            bf = h(n.left) - h(n.right)
            color = "#cfe8ff" if abs(bf) <= 1 else "#ffb3b3"
            label = f"{n.timestamp}\\n{n.temp}°C\\nbf={bf}"
            lines.append(f'{my_id} [label="{label}", fillcolor="{color}"];')
            left_id = rec(n.left)
            right_id = rec(n.right)
            if left_id:
                lines.append(f"{my_id} -> {left_id};")
            if right_id:
                lines.append(f"{my_id} -> {right_id};")
            return my_id

        rec(node)
    lines.append("}")
    return "\n".join(lines)


if page == "Dashboard":
    st.subheader("Region Overview — Array[7]")
    cols = st.columns(7)
    rows = []
    for i, region in enumerate(REGIONS):
        count = manager.region_count(region) if hasattr(manager, "region_count") else "?"
        rows.append({"Index": i, "Region": region, "Readings": count})
        with cols[i]:
            st.metric(region, count)

    st.divider()
    st.subheader("Readings per Region")
    df = pd.DataFrame(rows)
    st.bar_chart(df.set_index("Region")["Readings"])

    st.divider()
    st.subheader("Runtime Architecture")
    st.code(
        "Streamlit UI\n"
        "   |\n"
        "RegionManager\n"
        "   |\n"
        "Array[7]  -- one root per fixed IMD region\n"
        "   |\n"
        "Selected AVL Tree\n"
        "   |\n"
        "Timestamp-keyed nodes\n"
        "   |\n"
        "Insert / Search / Range Query / Delete + Rotations + Rebalancing",
        language=None,
    )

elif page == "Insert Reading":
    st.subheader("Insert a New Reading")
    with st.form("insert_form"):
        c1, c2, c3 = st.columns(3)
        region = c1.selectbox("Region", REGIONS)
        date_val = c2.date_input("Date", datetime.date(2024, 6, 15))
        temp = c3.number_input("Max Temperature (°C)", min_value=-10.0, max_value=60.0, value=38.0, step=0.1)
        submitted = st.form_submit_button("Insert Reading")
    if submitted:
        ts = date_val.strftime("%Y-%m-%d")
        manager.insert_reading(region, ts, temp)
        st.success(f"Inserted {ts} → {temp}°C into **{region}**  (O(log n) insert + rebalance)")

elif page == "Search Reading":
    st.subheader("Search for an Exact Reading (Point Query)")
    c1, c2 = st.columns(2)
    region = c1.selectbox("Region", REGIONS)
    date_val = c2.date_input("Date", datetime.date(2024, 6, 15), key="search_date")
    if st.button("Search"):
        ts = date_val.strftime("%Y-%m-%d")
        result = manager.search_reading(region, ts)
        if result:
            st.success(f"Found: {result['timestamp']} → {result['temperature']}°C in {region}")
        else:
            st.warning(f"No reading found for {ts} in {region}.")
        st.caption("O(log n) — one root-to-leaf path.")

elif page == "Range Query":
    st.subheader("Range Query")
    c1, c2, c3 = st.columns(3)
    region = c1.selectbox("Region", REGIONS)
    start = c2.date_input("Start date", datetime.date(2024, 1, 1))
    end = c3.date_input("End date", datetime.date(2024, 12, 31))
    if st.button("Run Range Query"):
        results = manager.range_query(region, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            st.caption(f"O(log n + k) — k = {len(results)} records returned")
        else:
            st.info("No readings found in that range.")

elif page == "Delete Reading":
    st.subheader("Delete a Reading")
    c1, c2 = st.columns(2)
    region = c1.selectbox("Region", REGIONS)
    date_val = c2.date_input("Date", datetime.date(2024, 6, 15), key="delete_date")
    if st.button("Delete Reading", type="primary"):
        ts = date_val.strftime("%Y-%m-%d")
        existed = manager.delete_reading(region, ts)
        if existed:
            st.success(f"Deleted {ts} from {region}.")
        else:
            st.warning(f"No reading found for {ts} in {region} — nothing deleted.")
        st.caption("O(log n) — BST delete + rebalance.")

elif page == "Tree Visualization":
    st.subheader("AVL Tree Visualization")
    region = st.selectbox("Region to visualize", REGIONS)
    if hasattr(manager, "get_root"):
        root = manager.get_root(region)
        dot = build_dot(root, region.replace(" ", "_"))
        st.graphviz_chart(dot)
        st.caption(
            "Each node shows timestamp / temperature / balance factor (bf). "
            "Blue = balanced (|bf| ≤ 1). Red would flag a temporary imbalance."
        )
    else:
        st.info("Connect the real dsa.region_manager (with a get_root(region) method) to enable this view.")

elif page == "About the Design":
    st.subheader("Chosen Data Structure")
    st.write("**Array[7] of AVL Trees, keyed by timestamp** — one AVL tree per fixed IMD region.")
    comp_df = pd.DataFrame(
        {
            "Operation": ["Insert", "Point Search", "Range Query", "Delete", "Space"],
            "Complexity": ["O(log n)", "O(log n)", "O(log n + k)", "O(log n)", "O(n)"],
            "Reason": [
                "AVL remains height-balanced.",
                "Binary-search property on timestamp.",
                "Reach relevant range efficiently, report k records.",
                "BST deletion followed by AVL rebalancing.",
                "One node per stored temperature record.",
            ],
        }
    )
    st.table(comp_df)
    st.write(
        "Region selection is **O(1)** since there are only 7 fixed regions; "
        "all logarithmic cost comes from AVL tree operations."
    )
