import streamlit as st
import pandas as pd
import numpy as np


def show_inventory_risk(df):

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("🚨 Inventory Risk")

    st.markdown(
        """
        Identify **inventory risk** using stockout conditions,
        optimized reorder points, safety stock, and demand
        variability.
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
        "Stockout_Flag",
        "Units_Sold",
        "Demand_Forecast",
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

    risk_df = df.copy()

    # =========================================================
    # DEMAND STATISTICS
    # =========================================================

    demand_stats = (
        risk_df
        .groupby(
            ["SKU_ID", "Warehouse_ID"],
            as_index=False
        )
        .agg(
            Avg_Daily_Demand=("Units_Sold", "mean"),
            Demand_Std=("Units_Sold", "std")
        )
    )

    demand_stats["Demand_Std"] = (
        demand_stats["Demand_Std"]
        .fillna(0)
    )

    risk_df = risk_df.merge(
        demand_stats,
        on=["SKU_ID", "Warehouse_ID"],
        how="left"
    )

    # =========================================================
    # SAFETY STOCK
    # =========================================================

    # 95% service level
    z_score = 1.645

    risk_df["Safety_Stock"] = (
        z_score
        * risk_df["Demand_Std"]
        * np.sqrt(
            risk_df["Supplier_Lead_Time_Days"]
            .clip(lower=0)
        )
    )

    # =========================================================
    # LEAD TIME DEMAND
    # =========================================================

    risk_df["Lead_Time_Demand"] = (
        risk_df["Avg_Daily_Demand"]
        * risk_df["Supplier_Lead_Time_Days"]
    )

    # =========================================================
    # OPTIMIZED ROP
    # =========================================================

    risk_df["Optimized_ROP"] = (
        risk_df["Lead_Time_Demand"]
        + risk_df["Safety_Stock"]
    )

    # =========================================================
    # DEMAND VARIABILITY
    # =========================================================

    risk_df["Demand_CV"] = np.where(
        risk_df["Avg_Daily_Demand"] > 0,
        risk_df["Demand_Std"]
        / risk_df["Avg_Daily_Demand"],
        0
    )

    # =========================================================
    # RISK SCORE
    # =========================================================

    risk_df["Risk_Score"] = 0

    # Stockout
    risk_df.loc[
        risk_df["Stockout_Flag"] == 1,
        "Risk_Score"
    ] += 40

    # Inventory below optimized ROP
    risk_df.loc[
        risk_df["Inventory_Level"]
        < risk_df["Optimized_ROP"],
        "Risk_Score"
    ] += 30

    # Inventory below safety stock
    risk_df.loc[
        risk_df["Inventory_Level"]
        < risk_df["Safety_Stock"],
        "Risk_Score"
    ] += 20

    # High demand variability
    risk_df.loc[
        risk_df["Demand_CV"] > 1,
        "Risk_Score"
    ] += 10

    # =========================================================
    # RISK CATEGORY
    # =========================================================

    risk_df["Risk_Level"] = np.select(
        [
            risk_df["Risk_Score"] >= 70,
            risk_df["Risk_Score"] >= 40,
            risk_df["Risk_Score"] >= 20
        ],
        [
            "🔴 Critical",
            "🟠 High",
            "🟡 Medium"
        ],
        default="🟢 Low"
    )

    # =========================================================
    # RISK REASON
    # =========================================================

    def get_risk_reason(row):

        reasons = []

        if row["Stockout_Flag"] == 1:
            reasons.append("Stockout")

        if row["Inventory_Level"] < row["Optimized_ROP"]:
            reasons.append("Below ROP")

        if row["Inventory_Level"] < row["Safety_Stock"]:
            reasons.append("Below Safety Stock")

        if row["Demand_CV"] > 1:
            reasons.append("High Demand Variability")

        if not reasons:
            return "No major risk"

        return ", ".join(reasons)

    risk_df["Risk_Reason"] = risk_df.apply(
        get_risk_reason,
        axis=1
    )

    # =========================================================
    # KPI SECTION
    # =========================================================

    st.subheader("🚨 Inventory Risk Overview")

    critical_count = (
        risk_df["Risk_Level"]
        .eq("🔴 Critical")
        .sum()
    )

    high_count = (
        risk_df["Risk_Level"]
        .eq("🟠 High")
        .sum()
    )

    medium_count = (
        risk_df["Risk_Level"]
        .eq("🟡 Medium")
        .sum()
    )

    low_count = (
        risk_df["Risk_Level"]
        .eq("🟢 Low")
        .sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🔴 Critical Risk",
            f"{critical_count:,}"
        )

    with col2:
        st.metric(
            "🟠 High Risk",
            f"{high_count:,}"
        )

    with col3:
        st.metric(
            "🟡 Medium Risk",
            f"{medium_count:,}"
        )

    with col4:
        st.metric(
            "🟢 Low Risk",
            f"{low_count:,}"
        )

    st.divider()

    # =========================================================
    # RISK FILTER
    # =========================================================

    st.subheader("🔍 Risk Filter")

    selected_risk = st.multiselect(
        "Select Risk Level",
        options=[
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

    filtered_risk = risk_df[
        risk_df["Risk_Level"].isin(selected_risk)
    ].copy()

    # =========================================================
    # RISK SCORE DISTRIBUTION
    # =========================================================

    st.subheader("📊 Risk Distribution")

    risk_distribution = (
        risk_df["Risk_Level"]
        .value_counts()
        .reindex(
            [
                "🔴 Critical",
                "🟠 High",
                "🟡 Medium",
                "🟢 Low"
            ],
            fill_value=0
        )
    )

    st.bar_chart(risk_distribution)

    # =========================================================
    # HIGH-RISK INVENTORY TABLE
    # =========================================================

    st.divider()

    st.subheader("🚨 High-Risk Inventory")

    display_columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Inventory_Level",
        "Avg_Daily_Demand",
        "Demand_Std",
        "Demand_CV",
        "Safety_Stock",
        "Reorder_Point",
        "Optimized_ROP",
        "Risk_Score",
        "Risk_Level",
        "Risk_Reason"
    ]

    display_df = (
        filtered_risk[display_columns]
        .sort_values(
            "Risk_Score",
            ascending=False
        )
    )

    st.dataframe(
        display_df.style.format({
            "Inventory_Level": "{:,.0f}",
            "Avg_Daily_Demand": "{:,.2f}",
            "Demand_Std": "{:,.2f}",
            "Demand_CV": "{:.2f}",
            "Safety_Stock": "{:,.0f}",
            "Reorder_Point": "{:,.0f}",
            "Optimized_ROP": "{:,.0f}",
            "Risk_Score": "{:,.0f}"
        }),
        use_container_width=True
    )

    # =========================================================
    # TOP RISK ITEMS
    # =========================================================

    st.divider()

    st.subheader("🔥 Top 10 Critical Inventory Risks")

    top_risk = (
        risk_df
        .sort_values(
            "Risk_Score",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_risk[
            [
                "SKU_ID",
                "Warehouse_ID",
                "Inventory_Level",
                "Optimized_ROP",
                "Risk_Score",
                "Risk_Level",
                "Risk_Reason"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # =========================================================
    # RISK BY WAREHOUSE
    # =========================================================

    st.divider()

    st.subheader("🏭 Risk by Warehouse")

    warehouse_risk = (
        risk_df
        .groupby("Warehouse_ID")
        .agg(
            Total_Items=("SKU_ID", "count"),
            Critical_Risk=(
                "Risk_Level",
                lambda x: (x == "🔴 Critical").sum()
            ),
            High_Risk=(
                "Risk_Level",
                lambda x: (x == "🟠 High").sum()
            ),
            Avg_Risk_Score=("Risk_Score", "mean")
        )
        .reset_index()
    )

    warehouse_risk["Total_High_Risk"] = (
        warehouse_risk["Critical_Risk"]
        + warehouse_risk["High_Risk"]
    )

    st.dataframe(
        warehouse_risk.style.format({
            "Total_Items": "{:,.0f}",
            "Critical_Risk": "{:,.0f}",
            "High_Risk": "{:,.0f}",
            "Avg_Risk_Score": "{:.2f}",
            "Total_High_Risk": "{:,.0f}"
        }),
        use_container_width=True
    )

    # =========================================================
    # DOWNLOAD
    # =========================================================

    st.divider()

    csv = risk_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Inventory Risk Report",
        data=csv,
        file_name="inventory_risk_report.csv",
        mime="text/csv"
    )