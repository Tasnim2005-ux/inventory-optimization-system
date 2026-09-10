import streamlit as st
import pandas as pd

from data_loader import load_data
from pages.home import show_home
from pages.executive_dashboard import show_executive_dashboard
from pages.data_overview import show_data_overview
from pages.abc_xyz_analysis import show_abc_xyz_analysis
from pages.safety_stock_rop import show_safety_stock_rop
from pages.eoq_cost_optimization import show_eoq_cost_optimization
from pages.supplier_performance import show_supplier_performance
from pages.warehouse_performance import show_warehouse_performance
from pages.inventory_risk import show_inventory_risk
from pages.replenishment import show_replenishment
from pages.optimization_impact import show_optimization_impact


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Inventory Optimization System",
    page_icon="📦",
    layout="wide"
)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

page = st.sidebar.radio(
    "Navigate to",
    [
        "🏠 Home",
        "📊 Executive Dashboard",
        "📊 Data Overview",
        "📦 ABC–XYZ Analysis",
        "🛡️ Safety Stock & ROP",
        "💰 EOQ & Cost Optimization",
        "🚚 Supplier Performance",
        "🏭 Warehouse Performance",
        "🚨 Inventory Risk",
        "🔄 Replenishment",
        "📈 Optimization Impact"
    ]
)


# =========================================================
# LOAD DATA
# =========================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "supply_chain_dataset1.csv"


@st.cache_data
def get_inventory_data():
    return load_data(DATA_PATH)


df = get_inventory_data()
filtered_df = df.copy()

# =========================================================
# PAGE ROUTING
# =========================================================

if page == "🏠 Home":
    show_home()

elif page == "📊 Executive Dashboard":
    show_executive_dashboard(filtered_df)

elif page == "📊 Data Overview":
    show_data_overview(filtered_df)

elif page == "📦 ABC–XYZ Analysis":
    show_abc_xyz_analysis(filtered_df)

elif page == "🛡️ Safety Stock & ROP":
    show_safety_stock_rop(filtered_df)

elif page == "💰 EOQ & Cost Optimization":
    show_eoq_cost_optimization(filtered_df)

elif page == "🚚 Supplier Performance":
    show_supplier_performance(filtered_df)

elif page == "🏭 Warehouse Performance":
    show_warehouse_performance(filtered_df)

elif page == "🚨 Inventory Risk":
    show_inventory_risk(filtered_df)

elif page == "🔄 Replenishment":
    show_replenishment(filtered_df)

elif page == "📈 Optimization Impact":
    show_optimization_impact(filtered_df)
# =========================================================
# GLOBAL DATA FILTERS
# =========================================================

st.sidebar.divider()
st.sidebar.subheader("🔎 Data Filters")
# Reset Filters Button
if st.sidebar.button("🔄 Reset Filters"):
    st.session_state["warehouse_filter"] = "All"
    st.session_state["region_filter"] = "All"
    st.session_state["supplier_filter"] = "All"
    st.session_state["sku_filter"] = "All"
    st.rerun()
filtered_df = df.copy()

# Warehouse Filter
if "Warehouse_ID" in df.columns:
    warehouses = ["All"] + sorted(
        df["Warehouse_ID"].dropna().unique().tolist()
    )

    selected_warehouse = st.sidebar.selectbox(
        "🏭 Warehouse",
        warehouses,
        key="warehouse_filter"
    )

    if selected_warehouse != "All":
        filtered_df = filtered_df[
            filtered_df["Warehouse_ID"] == selected_warehouse
        ]


# Region Filter
if "Region" in df.columns:
    regions = ["All"] + sorted(
        df["Region"].dropna().unique().tolist()
    )

    selected_region = st.sidebar.selectbox(
        "🌍 Region",
        regions,
        key="region_filter"
    )

    if selected_region != "All":
        filtered_df = filtered_df[
            filtered_df["Region"] == selected_region
        ]

# Supplier Filter
if "Supplier_ID" in df.columns:
    suppliers = ["All"] + sorted(
        df["Supplier_ID"].dropna().unique().tolist()
    )

    selected_supplier = st.sidebar.selectbox(
        "🚚 Supplier",
        suppliers,
        key="supplier_filter"
    )

    if selected_supplier != "All":
        filtered_df = filtered_df[
            filtered_df["Supplier_ID"] == selected_supplier
        ]

            
# SKU Filter
if "SKU_ID" in df.columns:
    skus = ["All"] + sorted(
        df["SKU_ID"].dropna().unique().tolist()
    )

    selected_sku = st.sidebar.selectbox(
        "📦 SKU",
        skus,
        key="sku_filter"
    )

    if selected_sku != "All":
        filtered_df = filtered_df[
            filtered_df["SKU_ID"] == selected_sku
        ]



# Date Range Filter
if "Date" in df.columns:

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    filtered_df["Date"] = pd.to_datetime(
        filtered_df["Date"],
        errors="coerce"
    )

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    selected_dates = st.sidebar.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(selected_dates) == 2:

        start_date, end_date = selected_dates

        filtered_df = filtered_df[
            (filtered_df["Date"].dt.date >= start_date) &
            (filtered_df["Date"].dt.date <= end_date)
        ]
# Filter Summary
st.sidebar.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} records"
)                        