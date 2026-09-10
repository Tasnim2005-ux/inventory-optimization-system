import streamlit as st
import pandas as pd
import numpy as np

from inventory_moduls import (
    calculate_safety_stock,
    calculate_rop
)


def show_safety_stock_rop(df):

    st.title("🛡️ Safety Stock & Reorder Point Optimization")

    st.markdown(
        """
        ### Inventory Protection & Replenishment Control

        This module calculates **Safety Stock** and **Optimized Reorder Point (ROP)**
        based on demand variability, supplier lead time, and target service level.
        """
    )

    st.divider()

    # =========================================================
    # SERVICE LEVEL
    # =========================================================

    st.subheader("🎯 Target Service Level")

    service_level = st.selectbox(
        "Select Target Service Level",
        [90, 95, 97.5, 99],
        index=1
    )

    z_values = {
        90: 1.282,
        95: 1.645,
        97.5: 1.960,
        99: 2.326
    }

    z_score = z_values[service_level]

    st.info(
        f"Target Service Level: {service_level}%  |  "
        f"Z-score: {z_score}"
    )

    # =========================================================
    # DATA PREPARATION
    # =========================================================

    work_df = df.copy()

    work_df["Date"] = pd.to_datetime(
        work_df["Date"],
        errors="coerce"
    )

    # =========================================================
    # DEMAND STATISTICS
    # =========================================================

    demand_stats = (
        work_df
        .groupby(["SKU_ID", "Warehouse_ID"])["Units_Sold"]
        .agg(
            Avg_Daily_Demand="mean",
            Demand_Std="std"
        )
        .reset_index()
    )

    demand_stats["Demand_Std"] = (
        demand_stats["Demand_Std"]
        .fillna(0)
    )

    work_df = work_df.merge(
        demand_stats,
        on=["SKU_ID", "Warehouse_ID"],
        how="left"
    )

    # =========================================================
    # LEAD TIME DEMAND
    # =========================================================

    work_df["Lead_Time_Demand"] = (
        work_df["Avg_Daily_Demand"]
        * work_df["Supplier_Lead_Time_Days"]
    )

    # =========================================================
    # SAFETY STOCK
    # =========================================================

    work_df["Safety_Stock"] = work_df.apply(
        lambda row: calculate_safety_stock(
            z_score,
            row["Demand_Std"],
            row["Supplier_Lead_Time_Days"]
        ),
        axis=1
    )

    # =========================================================
    # OPTIMIZED ROP
    # =========================================================

    work_df["Optimized_ROP"] = work_df.apply(
        lambda row: calculate_rop(
            row["Avg_Daily_Demand"],
            row["Supplier_Lead_Time_Days"],
            row["Safety_Stock"]
        ),
        axis=1
    )

    # =========================================================
    # CURRENT ROP COMPARISON
    # =========================================================

    if "Reorder_Point" in work_df.columns:

        work_df["ROP_Difference"] = (
            work_df["Optimized_ROP"]
            - work_df["Reorder_Point"]
        )

    # =========================================================
    # KPI SUMMARY
    # =========================================================

    st.subheader("📊 Safety Stock & ROP Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Average Safety Stock",
            f"{work_df['Safety_Stock'].mean():,.1f}"
        )

    with col2:
        st.metric(
            "Average Lead-Time Demand",
            f"{work_df['Lead_Time_Demand'].mean():,.1f}"
        )

    with col3:
        st.metric(
            "Average Optimized ROP",
            f"{work_df['Optimized_ROP'].mean():,.1f}"
        )

    with col4:

        if "ROP_Difference" in work_df.columns:
            st.metric(
                "Average ROP Difference",
                f"{work_df['ROP_Difference'].mean():,.1f}"
            )
        else:
            st.metric(
                "Average ROP Difference",
                "N/A"
            )

    st.divider()

    # =========================================================
    # INVENTORY STATUS
    # =========================================================

    def inventory_status(row):

        if row["Inventory_Level"] < row["Optimized_ROP"]:
            return "🔴 Reorder"

        elif row["Inventory_Level"] <= row["Optimized_ROP"] * 1.10:
            return "🟡 Monitor"

        else:
            return "🟢 Healthy"

    work_df["Inventory_Status"] = (
        work_df.apply(
            inventory_status,
            axis=1
        )
    )

    # =========================================================
    # STATUS SUMMARY
    # =========================================================

    st.subheader("🚦 Inventory Status")

    status_summary = (
        work_df["Inventory_Status"]
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Observations")
    )

    st.dataframe(
        status_summary,
        use_container_width=True,
        hide_index=True
    )

    # =========================================================
    # OPTIMIZATION DETAILS
    # =========================================================

    st.subheader("🔎 Safety Stock & ROP Details")

    detail_columns = [
        "Date",
        "SKU_ID",
        "Warehouse_ID",
        "Supplier_ID",
        "Inventory_Level",
        "Avg_Daily_Demand",
        "Demand_Std",
        "Supplier_Lead_Time_Days",
        "Lead_Time_Demand",
        "Safety_Stock",
        "Optimized_ROP",
        "Inventory_Status"
    ]

    if "Reorder_Point" in work_df.columns:
        detail_columns.extend(
            [
                "Reorder_Point",
                "ROP_Difference"
            ]
        )

    st.dataframe(
        work_df[detail_columns].head(100),
        use_container_width=True,
        hide_index=True
    )