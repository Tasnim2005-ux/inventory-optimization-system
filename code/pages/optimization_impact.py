import streamlit as st
import pandas as pd
import numpy as np

from inventory_moduls import (
    calculate_eoq,
    calculate_annual_ordering_cost,
    calculate_annual_holding_cost
)


def show_optimization_impact(df):

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("📈 Optimization Impact")

    st.markdown(
        """
        Compare the **current inventory policy** with the
        **optimized inventory policy** to measure potential
        improvements in reorder points, order quantities, and
        inventory cost.
        """
    )

    st.divider()

    # =========================================================
    # REQUIRED COLUMNS
    # =========================================================

    required_columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Inventory_Level",
        "Units_Sold",
        "Unit_Cost",
        "Supplier_Lead_Time_Days",
        "Reorder_Point"
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
    # PAGE-LOCAL DATA
    # =========================================================

    impact_df = df.copy()

    # =========================================================
    # DEMAND STATISTICS
    # =========================================================

    demand_stats = (
        impact_df
        .groupby(
            ["SKU_ID", "Warehouse_ID"],
            as_index=False
        )
        .agg(
            Annual_Demand=("Units_Sold", "sum"),
            Avg_Daily_Demand=("Units_Sold", "mean"),
            Demand_Std=("Units_Sold", "std"),
            Avg_Unit_Cost=("Unit_Cost", "mean"),
            Avg_Lead_Time=(
                "Supplier_Lead_Time_Days",
                "mean"
            )
        )
    )

    demand_stats["Demand_Std"] = (
        demand_stats["Demand_Std"]
        .fillna(0)
    )

    # =========================================================
    # SAFETY STOCK & OPTIMIZED ROP
    # =========================================================

    z_score = 1.645

    demand_stats["Safety_Stock"] = (
        z_score
        * demand_stats["Demand_Std"]
        * np.sqrt(
            demand_stats["Avg_Lead_Time"].clip(lower=0)
        )
    )

    demand_stats["Lead_Time_Demand"] = (
        demand_stats["Avg_Daily_Demand"]
        * demand_stats["Avg_Lead_Time"]
    )

    demand_stats["Optimized_ROP"] = (
        demand_stats["Lead_Time_Demand"]
        + demand_stats["Safety_Stock"]
    )

    # =========================================================
    # CURRENT ROP
    # =========================================================

    current_rop = (
        impact_df
        .groupby(
            ["SKU_ID", "Warehouse_ID"],
            as_index=False
        )
        .agg(
            Current_ROP=("Reorder_Point", "mean"),
            Current_Inventory=("Inventory_Level", "mean")
        )
    )

    # =========================================================
    # MERGE
    # =========================================================

    impact = demand_stats.merge(
        current_rop,
        on=["SKU_ID", "Warehouse_ID"],
        how="left"
    )

    # =========================================================
    # ROP IMPACT
    # =========================================================

    impact["ROP_Change"] = (
        impact["Optimized_ROP"]
        - impact["Current_ROP"]
    )

    impact["ROP_Improvement_%"] = np.where(
        impact["Current_ROP"] != 0,
        (
            impact["ROP_Change"]
            / impact["Current_ROP"].abs()
        ) * 100,
        0
    )

    # =========================================================
    # EOQ CALCULATION
    # =========================================================

    ordering_cost = 50.0
    holding_rate = 20.0

    impact["Holding_Cost_Per_Unit"] = (
        impact["Avg_Unit_Cost"]
        * holding_rate
        / 100
    )

    impact["EOQ"] = impact.apply(
        lambda row: calculate_eoq(
            row["Annual_Demand"],
            ordering_cost,
            row["Holding_Cost_Per_Unit"]
        ),
        axis=1
    )

    impact["EOQ"] = (
        impact["EOQ"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    # =========================================================
    # CURRENT ORDER QUANTITY
    # =========================================================

    # Current reorder point is used as a proxy for the
    # current replenishment quantity when actual order
    # quantity is not available in the dataset.

    impact["Current_Order_Qty"] = (
        impact["Current_ROP"]
    )

    # =========================================================
    # ORDER QUANTITY IMPACT
    # =========================================================

    impact["Order_Qty_Change"] = (
        impact["EOQ"]
        - impact["Current_Order_Qty"]
    )

    impact["Order_Qty_Improvement_%"] = np.where(
        impact["Current_Order_Qty"] != 0,
        (
            impact["Order_Qty_Change"]
            / impact["Current_Order_Qty"].abs()
        ) * 100,
        0
    )

    # =========================================================
    # CURRENT INVENTORY COST PROXY
    # =========================================================

    impact["Current_Ordering_Cost"] = (
        np.where(
            impact["Current_Order_Qty"] > 0,
            (
                impact["Annual_Demand"]
                / impact["Current_Order_Qty"]
            ) * ordering_cost,
            0
        )
    )

    impact["Current_Holding_Cost"] = (
        impact["Current_Order_Qty"]
        / 2
        * impact["Holding_Cost_Per_Unit"]
    )

    impact["Current_Total_Cost"] = (
        impact["Current_Ordering_Cost"]
        + impact["Current_Holding_Cost"]
    )

    # =========================================================
    # OPTIMIZED INVENTORY COST
    # =========================================================

    impact["Optimized_Ordering_Cost"] = (
        impact.apply(
            lambda row: calculate_annual_ordering_cost(
                row["Annual_Demand"],
                ordering_cost,
                row["EOQ"]
            ),
            axis=1
        )
    )

    impact["Optimized_Holding_Cost"] = (
        impact.apply(
            lambda row: calculate_annual_holding_cost(
                row["EOQ"],
                row["Holding_Cost_Per_Unit"]
            ),
            axis=1
        )
    )

    impact["Optimized_Total_Cost"] = (
        impact["Optimized_Ordering_Cost"]
        + impact["Optimized_Holding_Cost"]
    )

    # =========================================================
    # COST SAVING
    # =========================================================

    impact["Potential_Cost_Saving"] = (
        impact["Current_Total_Cost"]
        - impact["Optimized_Total_Cost"]
    )

    # =========================================================
    # KPI SECTION
    # =========================================================

    st.subheader("📊 Optimization Impact Overview")

    avg_current_rop = impact["Current_ROP"].mean()
    avg_optimized_rop = impact["Optimized_ROP"].mean()

    total_current_cost = (
        impact["Current_Total_Cost"].sum()
    )

    total_optimized_cost = (
        impact["Optimized_Total_Cost"].sum()
    )

    total_saving = (
        impact["Potential_Cost_Saving"].sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Current Avg ROP",
            f"{avg_current_rop:,.0f}"
        )

    with col2:
        st.metric(
            "Optimized Avg ROP",
            f"{avg_optimized_rop:,.0f}",
            delta=f"{avg_optimized_rop - avg_current_rop:,.0f}"
        )

    with col3:
        st.metric(
            "Current Inventory Cost",
            f"${total_current_cost:,.0f}"
        )

    with col4:
        st.metric(
            "Potential Cost Saving",
            f"${total_saving:,.0f}"
        )

    st.divider()

    # =========================================================
    # ROP COMPARISON
    # =========================================================

    st.subheader("🔄 Current vs Optimized ROP")

    rop_comparison = pd.DataFrame({
        "Policy": [
            "Current ROP",
            "Optimized ROP"
        ],
        "Average ROP": [
            avg_current_rop,
            avg_optimized_rop
        ]
    })

    st.bar_chart(
        rop_comparison.set_index("Policy")
    )

    # =========================================================
    # COST COMPARISON
    # =========================================================

    st.divider()

    st.subheader("💰 Inventory Cost Comparison")

    cost_comparison = pd.DataFrame({
        "Policy": [
            "Current Policy",
            "Optimized Policy"
        ],
        "Total Cost": [
            total_current_cost,
            total_optimized_cost
        ]
    })

    st.bar_chart(
        cost_comparison.set_index("Policy")
    )

    # =========================================================
    # OPTIMIZATION TABLE
    # =========================================================

    st.divider()

    st.subheader("📋 SKU-Warehouse Optimization Impact")

    display_columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Current_ROP",
        "Optimized_ROP",
        "ROP_Change",
        "ROP_Improvement_%",
        "Current_Order_Qty",
        "EOQ",
        "Order_Qty_Change",
        "Order_Qty_Improvement_%",
        "Current_Total_Cost",
        "Optimized_Total_Cost",
        "Potential_Cost_Saving"
    ]

    display_df = (
        impact[display_columns]
        .sort_values(
            "Potential_Cost_Saving",
            ascending=False
        )
    )

    st.dataframe(
        display_df.style.format({
            "Current_ROP": "{:,.0f}",
            "Optimized_ROP": "{:,.0f}",
            "ROP_Change": "{:,.0f}",
            "ROP_Improvement_%": "{:.2f}%",
            "Current_Order_Qty": "{:,.0f}",
            "EOQ": "{:,.0f}",
            "Order_Qty_Change": "{:,.0f}",
            "Order_Qty_Improvement_%": "{:.2f}%",
            "Current_Total_Cost": "${:,.2f}",
            "Optimized_Total_Cost": "${:,.2f}",
            "Potential_Cost_Saving": "${:,.2f}"
        }),
        use_container_width=True
    )

    # =========================================================
    # TOP SAVING OPPORTUNITIES
    # =========================================================

    st.divider()

    st.subheader("💎 Top Cost-Saving Opportunities")

    top_saving = (
        impact
        .sort_values(
            "Potential_Cost_Saving",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_saving[
            [
                "SKU_ID",
                "Warehouse_ID",
                "Current_Total_Cost",
                "Optimized_Total_Cost",
                "Potential_Cost_Saving"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # =========================================================
    # NEGATIVE / POSITIVE IMPACT
    # =========================================================

    positive_saving = (
        impact["Potential_Cost_Saving"] > 0
    ).sum()

    negative_saving = (
        impact["Potential_Cost_Saving"] < 0
    ).sum()

    col1, col2 = st.columns(2)

    with col1:
        st.success(
            f"✅ {positive_saving:,} SKU-Warehouse combinations "
            "show potential cost savings."
        )

    with col2:
        st.warning(
            f"⚠️ {negative_saving:,} combinations may require "
            "further review."
        )

    # =========================================================
    # DOWNLOAD
    # =========================================================

    st.divider()

    csv = impact.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Optimization Impact Report",
        data=csv,
        file_name="optimization_impact_report.csv",
        mime="text/csv"
    )