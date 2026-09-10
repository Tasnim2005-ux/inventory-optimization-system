import streamlit as st
import pandas as pd
import numpy as np

from inventory_moduls import calculate_eoq


def show_replenishment(df):

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("🔄 Replenishment")

    st.markdown(
        """
        Determine **when to replenish inventory, how much to order,
        and which SKU-Warehouse combinations should receive priority**.
        """
    )

    st.divider()

    # =========================================================
    # REQUIRED COLUMNS
    # =========================================================

    required_columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Supplier_ID",
        "Inventory_Level",
        "Units_Sold",
        "Unit_Cost",
        "Supplier_Lead_Time_Days",
        "Reorder_Point",
        "Stockout_Flag"
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

    replenishment_df = df.copy()

    # =========================================================
    # DEMAND STATISTICS
    # =========================================================

    demand_stats = (
        replenishment_df
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
    # EOQ
    # =========================================================

    ordering_cost = 50.0
    holding_rate = 20.0

    demand_stats["Holding_Cost_Per_Unit"] = (
        demand_stats["Avg_Unit_Cost"]
        * holding_rate
        / 100
    )

    demand_stats["EOQ"] = demand_stats.apply(
        lambda row: calculate_eoq(
            row["Annual_Demand"],
            ordering_cost,
            row["Holding_Cost_Per_Unit"]
        ),
        axis=1
    )

    demand_stats["EOQ"] = (
        demand_stats["EOQ"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    # =========================================================
    # LATEST INVENTORY STATUS
    # =========================================================

    latest_date = None

    if "Date" in replenishment_df.columns:

        replenishment_df["Date"] = pd.to_datetime(
            replenishment_df["Date"],
            errors="coerce"
        )

        latest_date = replenishment_df["Date"].max()

        latest_inventory = (
            replenishment_df[
                replenishment_df["Date"] == latest_date
            ]
            .groupby(
                ["SKU_ID", "Warehouse_ID"],
                as_index=False
            )
            .agg(
                Inventory_Level=("Inventory_Level", "mean"),
                Supplier_ID=("Supplier_ID", "first"),
                Stockout_Flag=("Stockout_Flag", "max"),
                Current_ROP=("Reorder_Point", "mean")
            )
        )

    else:

        latest_inventory = (
            replenishment_df
            .groupby(
                ["SKU_ID", "Warehouse_ID"],
                as_index=False
            )
            .agg(
                Inventory_Level=("Inventory_Level", "mean"),
                Supplier_ID=("Supplier_ID", "first"),
                Stockout_Flag=("Stockout_Flag", "max"),
                Current_ROP=("Reorder_Point", "mean")
            )
        )

    # =========================================================
    # MERGE
    # =========================================================

    replenishment = demand_stats.merge(
        latest_inventory,
        on=["SKU_ID", "Warehouse_ID"],
        how="left"
    )

    # =========================================================
    # REPLENISHMENT DECISION
    # =========================================================

    replenishment["Reorder_Required"] = (
        replenishment["Inventory_Level"]
        < replenishment["Optimized_ROP"]
    )

    # Recommended Order Quantity
    replenishment["Recommended_Order_Qty"] = np.where(
        replenishment["Reorder_Required"],
        replenishment["EOQ"],
        0
    )

    # =========================================================
    # INVENTORY SHORTAGE
    # =========================================================

    replenishment["Inventory_Shortage"] = (
        replenishment["Optimized_ROP"]
        - replenishment["Inventory_Level"]
    )

    replenishment["Inventory_Shortage"] = (
        replenishment["Inventory_Shortage"]
        .clip(lower=0)
    )

    # =========================================================
    # PRIORITY
    # =========================================================

    replenishment["Priority_Score"] = 0

    # Stockout
    replenishment.loc[
        replenishment["Stockout_Flag"] == 1,
        "Priority_Score"
    ] += 40

    # Below ROP
    replenishment.loc[
        replenishment["Reorder_Required"],
        "Priority_Score"
    ] += 30

    # Severe shortage
    replenishment.loc[
        replenishment["Inventory_Level"]
        < replenishment["Safety_Stock"],
        "Priority_Score"
    ] += 20

    # High demand variability
    replenishment.loc[
        (
            replenishment["Demand_Std"]
            / replenishment["Avg_Daily_Demand"].replace(0, np.nan)
        ).fillna(0) > 1,
        "Priority_Score"
    ] += 10

    # =========================================================
    # PRIORITY CATEGORY
    # =========================================================

    replenishment["Priority"] = np.select(
        [
            replenishment["Priority_Score"] >= 70,
            replenishment["Priority_Score"] >= 40,
            replenishment["Priority_Score"] >= 20
        ],
        [
            "🔴 Critical",
            "🟠 High",
            "🟡 Medium"
        ],
        default="🟢 Low"
    )

    # =========================================================
    # RECOMMENDATION
    # =========================================================

    def get_recommendation(row):

        if row["Priority"] == "🔴 Critical":
            return "🚨 Immediate replenishment required"

        if row["Priority"] == "🟠 High":
            return "⚠️ Replenish as soon as possible"

        if row["Priority"] == "🟡 Medium":
            return "👀 Monitor and plan replenishment"

        return "✅ No immediate replenishment required"

    replenishment["Recommendation"] = (
        replenishment.apply(
            get_recommendation,
            axis=1
        )
    )

    # =========================================================
    # KPI SECTION
    # =========================================================

    st.subheader("📊 Replenishment Overview")

    reorder_items = (
        replenishment["Reorder_Required"].sum()
    )

    critical_items = (
        replenishment["Priority"]
        .eq("🔴 Critical")
        .sum()
    )

    high_items = (
        replenishment["Priority"]
        .eq("🟠 High")
        .sum()
    )

    total_order_qty = (
        replenishment["Recommended_Order_Qty"].sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🔄 Reorder Required",
            f"{reorder_items:,}"
        )

    with col2:
        st.metric(
            "🔴 Critical",
            f"{critical_items:,}"
        )

    with col3:
        st.metric(
            "🟠 High Priority",
            f"{high_items:,}"
        )

    with col4:
        st.metric(
            "📦 Recommended Order Qty",
            f"{total_order_qty:,.0f}"
        )

    if latest_date is not None:
        st.caption(
            f"Inventory status based on latest available date: "
            f"{latest_date.date()}"
        )

    st.divider()

    # =========================================================
    # FILTER
    # =========================================================

    st.subheader("🔍 Replenishment Filter")

    selected_priority = st.multiselect(
        "Select Priority",
        [
            "🔴 Critical",
            "🟠 High",
            "🟡 Medium",
            "🟢 Low"
        ],
        default=[
            "🔴 Critical",
            "🟠 High"
        ]
    )

    filtered_replenishment = replenishment[
        replenishment["Priority"].isin(
            selected_priority
        )
    ].copy()

    # =========================================================
    # REPLENISHMENT TABLE
    # =========================================================

    st.subheader("🔄 Replenishment Recommendations")

    display_columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Supplier_ID",
        "Inventory_Level",
        "Avg_Daily_Demand",
        "Safety_Stock",
        "Optimized_ROP",
        "EOQ",
        "Inventory_Shortage",
        "Recommended_Order_Qty",
        "Priority_Score",
        "Priority",
        "Recommendation"
    ]

    display_df = (
        filtered_replenishment[display_columns]
        .sort_values(
            "Priority_Score",
            ascending=False
        )
    )

    st.dataframe(
        display_df.style.format({
            "Inventory_Level": "{:,.0f}",
            "Avg_Daily_Demand": "{:,.2f}",
            "Safety_Stock": "{:,.0f}",
            "Optimized_ROP": "{:,.0f}",
            "EOQ": "{:,.0f}",
            "Inventory_Shortage": "{:,.0f}",
            "Recommended_Order_Qty": "{:,.0f}",
            "Priority_Score": "{:,.0f}"
        }),
        use_container_width=True
    )

    # =========================================================
    # CRITICAL REPLENISHMENT
    # =========================================================

    st.divider()

    st.subheader("🚨 Immediate Replenishment")

    critical_replenishment = (
        replenishment[
            replenishment["Priority"] == "🔴 Critical"
        ]
        .sort_values(
            "Priority_Score",
            ascending=False
        )
        .head(10)
    )

    if critical_replenishment.empty:

        st.success(
            "✅ No critical replenishment items found."
        )

    else:

        st.dataframe(
            critical_replenishment[
                [
                    "SKU_ID",
                    "Warehouse_ID",
                    "Supplier_ID",
                    "Inventory_Level",
                    "Optimized_ROP",
                    "EOQ",
                    "Recommended_Order_Qty",
                    "Priority_Score",
                    "Recommendation"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    # =========================================================
    # ORDER QUANTITY CHART
    # =========================================================

    st.divider()

    st.subheader("📦 Recommended Order Quantity")

    chart_data = (
        replenishment[
            replenishment["Recommended_Order_Qty"] > 0
        ]
        .sort_values(
            "Recommended_Order_Qty",
            ascending=False
        )
        .head(10)
    )

    if not chart_data.empty:

        chart_data["Item"] = (
            chart_data["SKU_ID"].astype(str)
            + " | "
            + chart_data["Warehouse_ID"].astype(str)
        )

        st.bar_chart(
            chart_data.set_index("Item")[
                "Recommended_Order_Qty"
            ]
        )

    else:

        st.info(
            "No replenishment quantity is currently recommended."
        )

    # =========================================================
    # DOWNLOAD
    # =========================================================

    st.divider()

    csv = replenishment.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Replenishment Report",
        data=csv,
        file_name="replenishment_report.csv",
        mime="text/csv"
    )