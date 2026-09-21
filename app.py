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
    "North India", "South India", "East India", "West India",
    "Central India", "Northeast India", "Islands",
]

st.set_page_config(page_title="Heatwave Monitoring — Array[7] of AVL Trees", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --ink: #17231f;
        --muted: #64736b;
        --paper: #f7f5ef;
        --panel: #fffdf8;
        --line: #dce2d8;
        --coral: #ef765d;
        --coral-dark: #c94f3e;
        --sage: #3d6b5d;
        --sun: #f3bb52;
    }

    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
        color: var(--ink);
    }

    .stApp {
        background: var(--paper);
        background-image: radial-gradient(#d8ded2 0.7px, transparent 0.7px);
        background-size: 18px 18px;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #17362e;
        border-right: 0;
        box-shadow: 8px 0 28px rgba(23, 35, 31, 0.08);
    }
    [data-testid="stSidebar"] * { color: #f5f1e6; }
    [data-testid="stSidebar"] h2 {
        color: #f5f1e6;
        font-size: 1.9rem !important;
        letter-spacing: -0.05em;
        margin-top: 1rem;
    }
    [data-testid="stSidebar"] [role="radio"],
    [data-testid="stSidebar"] input[type="radio"] {
        display: none;
    }
    [data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div > div:first-child {
        display: none;
    }
    [data-testid="stSidebar"] [data-testid="stRadioOption"] > div {
        border-radius: 8px;
        padding: 0.28rem 0.55rem;
        transition: background 160ms ease, transform 160ms ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadioOption"] > div:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateX(3px);
    }
    [data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked) > div {
        background: var(--coral);
    }
    [data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked) p {
        color: #ffffff !important;
        font-weight: 800;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.18); }

    .top-nav {
        background: #17362e;
        border-radius: 12px 12px 0 0;
        box-shadow: 0 10px 24px rgba(23, 35, 31, 0.14);
        color: #f5f1e6;
        padding: 0.45rem 1.1rem 0.2rem;
        margin: 0;
    }
    .top-nav-label {
        color: #f3bb52;
        font: 500 0.68rem 'DM Mono', monospace;
        letter-spacing: 0.12em;
        margin: 0.2rem 0 0.1rem;
        text-transform: uppercase;
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stRadio"]) {
        align-items: center;
    }
    .top-nav + div [data-testid="stRadio"] {
        background: #17362e;
        border-radius: 0 0 12px 12px;
        box-shadow: 0 10px 24px rgba(23, 35, 31, 0.14);
        margin: 0 0 2.7rem;
        padding: 0.2rem 1.1rem 0.8rem;
    }
    .top-nav + div [data-testid="stRadio"] label {
        color: #f5f1e6 !important;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .top-nav + div [data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.3rem;
    }
    .top-nav + div [data-testid="stRadio"] [role="radiogroup"] > div:has([role="radio"]) {
        border-radius: 7px;
        padding: 0.35rem 0.7rem;
        transition: background 160ms ease, color 160ms ease;
    }
    .top-nav + div [data-testid="stRadio"] [role="radiogroup"] > div:has([role="radio"]):hover {
        background: rgba(255, 253, 248, 0.12);
    }
    .top-nav + div [data-testid="stRadio"] [role="radio"] {
        display: none;
    }
    .top-nav + div [data-testid="stRadio"] [role="radiogroup"] > div:has([role="radio"][aria-checked="true"]) {
        background: var(--coral);
    }
    .top-nav + div [data-testid="stRadio"] [role="radiogroup"] > div:has([role="radio"][aria-checked="true"]) label {
        color: #ffffff !important;
    }
    .block-container {
        max-width: 1280px;
        padding: 2.8rem 4rem 4rem;
    }
    h1, h2, h3 { letter-spacing: -0.04em; color: var(--ink); }
    h1 { font-size: clamp(2.2rem, 4vw, 4.2rem) !important; line-height: 1.02 !important; }
    h2 { font-size: 1.65rem !important; }
    h3 { font-size: 1.15rem !important; }
    [data-testid="stCaptionContainer"] { color: var(--muted); }

    .eyebrow {
        color: var(--coral-dark);
        font: 500 0.72rem 'DM Mono', monospace;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.65rem;
    }
    .hero-copy {
        max-width: 680px;
        color: var(--muted);
        font-size: 1.02rem;
        line-height: 1.7;
        margin: 0.5rem 0 2.6rem;
    }
    .hero-copy strong { color: var(--sage); }
    .section-rule {
        height: 1px;
        background: var(--line);
        margin: 1.25rem 0 1.8rem;
    }
    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-top: 4px solid var(--coral);
        border-radius: 12px;
        padding: 1rem 1rem 0.85rem;
        min-height: 118px;
        box-shadow: 0 8px 24px rgba(23, 35, 31, 0.06);
        transition: transform 160ms ease, box-shadow 160ms ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(23, 35, 31, 0.12);
    }
    [data-testid="stMetricLabel"] p {
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 700;
        line-height: 1.2;
    }
    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-size: 2rem;
        font-weight: 800;
    }
    .stButton > button, [data-testid="stFormSubmitButton"] button {
        background: var(--coral);
        border: 0;
        border-radius: 7px;
        color: white;
        font-weight: 800;
        padding: 0.65rem 1.1rem;
        transition: background 160ms ease, transform 160ms ease;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
        background: var(--coral-dark);
        color: white;
        transform: translateY(-1px);
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 10px;
        overflow: hidden;
    }
    .stCodeBlock, [data-testid="stCode"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-left: 4px solid var(--sun);
        border-radius: 8px;
    }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--muted); }
    @media (max-width: 800px) {
        .block-container { padding: 2.3rem 1.25rem 3rem; }
        h1 { font-size: 2.4rem !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_manager():
    mgr = RegionManager()
    if hasattr(mgr, "seed_sample_data"):
        mgr.seed_sample_data()
    return mgr


manager = get_manager()

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

st.markdown('<div class="eyebrow">FIELD OPS / 07 REGIONS / LIVE INDEX</div>', unsafe_allow_html=True)
st.title("Heatwave Monitoring")
st.markdown(
    '<p class="hero-copy">A calm view of a restless climate. Track <strong>temperature readings</strong> '
    'across India with timestamp-keyed AVL trees built for quick decisions.</p>',
    unsafe_allow_html=True,
)


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
            label = f"{n.timestamp}\\n{n.max_temp}°C\\nbf={bf}"
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
    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    st.subheader("Regional pulse")
    st.caption("Stored readings by region · each index owns one self-balancing AVL tree")
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
            st.success(f"Found: {ts} → {result}°C in {region}")
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
