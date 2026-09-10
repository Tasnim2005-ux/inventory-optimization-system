import streamlit as st
import pandas as pd
import numpy as np

from inventory_moduls import (
    calculate_eoq,
    calculate_annual_ordering_cost,
    calculate_annual_holding_cost,
    calculate_inventory_cost
)


def show_eoq_cost_optimization(df):

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("💰 EOQ & Cost Optimization")

    st.markdown(
        """
        This page determines the **Economic Order Quantity (EOQ)**
        and estimates the inventory costs associated with ordering
        and holding inventory.
        """
    )

    st.divider()

    # =========================================================
    # REQUIRED COLUMNS CHECK
    # =========================================================

    required_columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Unit_Cost",
        "Units_Sold"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        st.error(
            f"❌ Missing required columns: {', '.join(missing_columns)}"
        )
        return

    # =========================================================
    # USER PARAMETERS
    # =========================================================

    st.subheader("⚙️ Cost Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        ordering_cost = st.number_input(
            "Ordering Cost per Order ($)",
            min_value=1.0,
            value=50.0,
            step=5.0
        )

    with col2:
        holding_rate = st.number_input(
            "Annual Holding Rate (%)",
            min_value=1.0,
            value=20.0,
            step=1.0
        )

    with col3:
        st.metric(
            "Holding Rate",
            f"{holding_rate:.1f}%"
        )

    st.divider()

    # =========================================================
    # SKU-WAREHOUSE LEVEL AGGREGATION
    # =========================================================

    eoq_df = (
        df.groupby(
            ["SKU_ID", "Warehouse_ID"],
            as_index=False
        )
        .agg(
            Annual_Demand=("Units_Sold", "sum"),
            Unit_Cost=("Unit_Cost", "mean")
        )
    )

    # =========================================================
    # ANNUAL HOLDING COST
    # =========================================================

    eoq_df["Annual_Holding_Cost_Per_Unit"] = (
        eoq_df["Unit_Cost"] * holding_rate / 100
    )

    # =========================================================
    # EOQ CALCULATION
    # =========================================================

    eoq_df["EOQ"] = np.sqrt(
        (
            2
            * eoq_df["Annual_Demand"]
            * ordering_cost
        )
        / eoq_df["Annual_Holding_Cost_Per_Unit"]
    )

    eoq_df["EOQ"] = eoq_df["EOQ"].replace(
        [np.inf, -np.inf],
        np.nan
    ).fillna(0)

    # =========================================================
    # INVENTORY COST CALCULATIONS
    # =========================================================

    eoq_df["Annual_Ordering_Cost"] = (
        eoq_df.apply(
            lambda row: calculate_annual_ordering_cost(
                row["Annual_Demand"],
                ordering_cost,
                row["EOQ"]
            ),
            axis=1
        )
    )

    eoq_df["Annual_Holding_Cost"] = (
        eoq_df.apply(
            lambda row: calculate_annual_holding_cost(
                row["EOQ"],
                row["Annual_Holding_Cost_Per_Unit"]
            ),
            axis=1
        )
    )

    eoq_df["Total_Inventory_Cost"] = (
        eoq_df["Annual_Ordering_Cost"]
        + eoq_df["Annual_Holding_Cost"]
    )

    # =========================================================
    # KPI SECTION
    # =========================================================

    st.subheader("📊 EOQ Optimization Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Average EOQ",
            f"{eoq_df['EOQ'].mean():,.0f}"
        )

    with col2:
        st.metric(
            "Total Annual Demand",
            f"{eoq_df['Annual_Demand'].sum():,.0f}"
        )

    with col3:
        st.metric(
            "Annual Ordering Cost",
            f"${eoq_df['Annual_Ordering_Cost'].sum():,.0f}"
        )

    with col4:
        st.metric(
            "Total Inventory Cost",
            f"${eoq_df['Total_Inventory_Cost'].sum():,.0f}"
        )

    st.divider()

    # =========================================================
    # EOQ TABLE
    # =========================================================

    st.subheader("📦 EOQ by SKU & Warehouse")

    display_columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Annual_Demand",
        "Unit_Cost",
        "Annual_Holding_Cost_Per_Unit",
        "EOQ",
        "Annual_Ordering_Cost",
        "Annual_Holding_Cost",
        "Total_Inventory_Cost"
    ]

    display_df = eoq_df[display_columns].copy()

    st.dataframe(
        display_df.style.format({
            "Annual_Demand": "{:,.0f}",
            "Unit_Cost": "${:,.2f}",
            "Annual_Holding_Cost_Per_Unit": "${:,.2f}",
            "EOQ": "{:,.0f}",
            "Annual_Ordering_Cost": "${:,.2f}",
            "Annual_Holding_Cost": "${:,.2f}",
            "Total_Inventory_Cost": "${:,.2f}"
        }),
        use_container_width=True
    )

    # =========================================================
    # COST ANALYSIS
    # =========================================================

    st.divider()

    st.subheader("💵 Cost Analysis")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Ordering vs Holding Cost")

        cost_summary = pd.DataFrame({
            "Cost Type": [
                "Ordering Cost",
                "Holding Cost"
            ],
            "Cost": [
                eoq_df["Annual_Ordering_Cost"].sum(),
                eoq_df["Annual_Holding_Cost"].sum()
            ]
        })

        st.bar_chart(
            cost_summary.set_index("Cost Type")
        )

    with col2:

        st.markdown("### Top Inventory Cost Items")

        top_cost = (
            eoq_df
            .sort_values(
                "Total_Inventory_Cost",
                ascending=False
            )
            .head(10)
        )

        st.bar_chart(
            top_cost.set_index("SKU_ID")[
                "Total_Inventory_Cost"
            ]
        )

    # =========================================================
    # DOWNLOAD
    # =========================================================

    st.divider()

    csv = eoq_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download EOQ Analysis",
        data=csv,
        file_name="eoq_cost_optimization.csv",
        mime="text/csv"
    )