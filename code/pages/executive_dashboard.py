import streamlit as st
import pandas as pd


def show_executive_dashboard(df):

    st.title("🎯 Executive Inventory Dashboard")

    st.markdown(
        """
        ### Inventory Optimization & Decision Support System

        Data-driven insights for inventory performance,
        risk assessment, and replenishment decisions.
        """
    )

    st.divider()

    # =====================================================
    # MANAGEMENT KPIs
    # =====================================================

    total_records = len(df)
    total_skus = df["SKU_ID"].nunique()
    total_warehouses = df["Warehouse_ID"].nunique()
    total_suppliers = df["Supplier_ID"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📋 Total Records",
            f"{total_records:,}"
        )

    with col2:
        st.metric(
            "📦 Unique SKUs",
            f"{total_skus:,}"
        )

    with col3:
        st.metric(
            "🏭 Warehouses",
            f"{total_warehouses:,}"
        )

    with col4:
        st.metric(
            "🚚 Suppliers",
            f"{total_suppliers:,}"
        )

    st.divider()

    # =====================================================
    # DATASET PERIOD
    # =====================================================

    st.subheader("📅 Dataset Period")

    if "Date" in df.columns:

        date_df = df.copy()

        date_df["Date"] = pd.to_datetime(
            date_df["Date"],
            errors="coerce"
        )

        start_date = date_df["Date"].min()
        end_date = date_df["Date"].max()

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Start Date",
                str(start_date.date())
            )

        with col2:
            st.metric(
                "End Date",
                str(end_date.date())
            )

    st.divider()

    # =====================================================
    # INVENTORY KPIs
    # =====================================================

    st.subheader("📦 Inventory Overview")

    total_inventory = df["Inventory_Level"].sum()

    inventory_value = (
        df["Inventory_Level"] *
        df["Unit_Cost"]
    ).sum()

    total_units_sold = df["Units_Sold"].sum()

    average_inventory = df["Inventory_Level"].mean()

    if average_inventory > 0:
        inventory_turnover = (
            total_units_sold /
            average_inventory
        )
    else:
        inventory_turnover = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📦 Inventory Units",
            f"{total_inventory:,.0f}"
        )

    with col2:
        st.metric(
            "💰 Inventory Value",
            f"${inventory_value:,.2f}"
        )

    with col3:
        st.metric(
            "📈 Units Sold",
            f"{total_units_sold:,.0f}"
        )

    with col4:
        st.metric
