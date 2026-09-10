import streamlit as st
import pandas as pd


def show_warehouse_performance(df):

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("🏭 Warehouse Performance")

    st.markdown(
        """
        Analyze warehouse performance using **inventory level,
        inventory value, sales volume, stockouts, and inventory
        coverage**.
        """
    )

    st.divider()

    # =========================================================
    # REQUIRED COLUMNS CHECK
    # =========================================================

    required_columns = [
        "Warehouse_ID",
        "SKU_ID",
        "Units_Sold",
        "Inventory_Level",
        "Stockout_Flag",
        "Unit_Cost"
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

    warehouse_data = df.copy()

    # Inventory Value
    warehouse_data["Inventory_Value"] = (
        warehouse_data["Inventory_Level"]
        * warehouse_data["Unit_Cost"]
    )

    # =========================================================
    # WAREHOUSE AGGREGATION
    # =========================================================

    warehouse_df = (
        warehouse_data
        .groupby("Warehouse_ID", as_index=False)
        .agg(
            Records=("Warehouse_ID", "size"),
            Unique_SKUs=("SKU_ID", "nunique"),
            Units_Sold=("Units_Sold", "sum"),
            Inventory_Units=("Inventory_Level", "sum"),
            Inventory_Value=("Inventory_Value", "sum"),
            Stockouts=("Stockout_Flag", "sum")
        )
    )

    # =========================================================
    # PERFORMANCE METRICS
    # =========================================================

    warehouse_df["Stockout_Rate"] = (
        warehouse_df["Stockouts"]
        / warehouse_df["Records"]
        * 100
    )

    warehouse_df["Inventory_Coverage"] = (
        warehouse_df["Inventory_Units"]
        / warehouse_df["Units_Sold"].replace(0, pd.NA)
    )

    warehouse_df["Inventory_Coverage"] = (
        warehouse_df["Inventory_Coverage"]
        .fillna(0)
    )

    # =========================================================
    # PERFORMANCE SCORE
    # =========================================================

    warehouse_df["Stockout_Score"] = (
        warehouse_df["Stockout_Rate"].rank(
            ascending=True,
            pct=True
        )
    )

    warehouse_df["Coverage_Score"] = (
        warehouse_df["Inventory_Coverage"].rank(
            ascending=True,
            pct=True
        )
    )

    warehouse_df["Value_Score"] = (
        warehouse_df["Inventory_Value"].rank(
            ascending=False,
            pct=True
        )
    )

    warehouse_df["Performance_Score"] = (
        (1 - warehouse_df["Stockout_Score"]) * 50
        + warehouse_df["Coverage_Score"] * 30
        + warehouse_df["Value_Score"] * 20
    )

    warehouse_df["Warehouse_Rank"] = (
        warehouse_df["Performance_Score"]
        .rank(ascending=False)
        .astype(int)
    )

    # =========================================================
    # PERFORMANCE CATEGORY
    # =========================================================

    warehouse_df["Performance"] = pd.cut(
        warehouse_df["Warehouse_Rank"],
        bins=[
            0,
            max(1, len(warehouse_df) * 0.25),
            max(2, len(warehouse_df) * 0.50),
            max(3, len(warehouse_df) * 0.75),
            len(warehouse_df)
        ],
        labels=[
            "🟢 Excellent",
            "🟡 Good",
            "🟠 Average",
            "🔴 Needs Improvement"
        ],
        include_lowest=True
    )

    # =========================================================
    # KPI SECTION
    # =========================================================

    st.subheader("📊 Warehouse Performance Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Warehouses",
            f"{warehouse_df['Warehouse_ID'].nunique():,}"
        )

    with col2:
        st.metric(
            "Inventory Units",
            f"{warehouse_df['Inventory_Units'].sum():,.0f}"
        )

    with col3:
        st.metric(
            "Inventory Value",
            f"${warehouse_df['Inventory_Value'].sum():,.0f}"
        )

    with col4:
        st.metric(
            "Stockout Rate",
            f"{warehouse_df['Stockout_Rate'].mean():.2f}%"
        )

    st.divider()

    # =========================================================
    # WAREHOUSE SCORECARD
    # =========================================================

    st.subheader("🏭 Warehouse Performance Scorecard")

    display_columns = [
        "Warehouse_ID",
        "Records",
        "Unique_SKUs",
        "Units_Sold",
        "Inventory_Units",
        "Inventory_Value",
        "Stockouts",
        "Stockout_Rate",
        "Inventory_Coverage",
        "Warehouse_Rank",
        "Performance"
    ]

    display_df = (
        warehouse_df[display_columns]
        .sort_values("Warehouse_Rank")
    )

    st.dataframe(
        display_df.style.format({
            "Records": "{:,.0f}",
            "Unique_SKUs": "{:,.0f}",
            "Units_Sold": "{:,.0f}",
            "Inventory_Units": "{:,.0f}",
            "Inventory_Value": "${:,.2f}",
            "Stockouts": "{:,.0f}",
            "Stockout_Rate": "{:.2f}%",
            "Inventory_Coverage": "{:.2f}",
            "Warehouse_Rank": "{:,.0f}"
        }),
        use_container_width=True
    )

    # =========================================================
    # CHARTS
    # =========================================================

    st.divider()

    st.subheader("📈 Warehouse Analysis")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Inventory Value by Warehouse")

        inventory_value_chart = (
            warehouse_df
            .sort_values(
                "Inventory_Value",
                ascending=False
            )
            .set_index("Warehouse_ID")[
                "Inventory_Value"
            ]
        )

        st.bar_chart(inventory_value_chart)

    with col2:

        st.markdown("### Stockout Rate by Warehouse")

        stockout_chart = (
            warehouse_df
            .sort_values(
                "Stockout_Rate",
                ascending=False
            )
            .set_index("Warehouse_ID")[
                "Stockout_Rate"
            ]
        )

        st.bar_chart(stockout_chart)

    # =========================================================
    # INVENTORY COVERAGE
    # =========================================================

    st.divider()

    st.subheader("📦 Inventory Coverage")

    coverage_chart = (
        warehouse_df
        .sort_values(
            "Inventory_Coverage",
            ascending=False
        )
        .set_index("Warehouse_ID")[
            "Inventory_Coverage"
        ]
    )

    st.bar_chart(coverage_chart)

    st.caption(
        "Inventory Coverage = Inventory Units ÷ Units Sold"
    )

    # =========================================================
    # BEST & WORST WAREHOUSES
    # =========================================================

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🏆 Best Performing Warehouses")

        best_warehouses = (
            warehouse_df
            .sort_values("Warehouse_Rank")
            .head(5)
        )

        st.dataframe(
            best_warehouses[
                [
                    "Warehouse_ID",
                    "Inventory_Value",
                    "Stockout_Rate",
                    "Inventory_Coverage",
                    "Warehouse_Rank",
                    "Performance"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    with col2:

        st.subheader("⚠️ Warehouses Needing Attention")

        weak_warehouses = (
            warehouse_df
            .sort_values(
                "Warehouse_Rank",
                ascending=False
            )
            .head(5)
        )

        st.dataframe(
            weak_warehouses[
                [
                    "Warehouse_ID",
                    "Inventory_Value",
                    "Stockout_Rate",
                    "Inventory_Coverage",
                    "Warehouse_Rank",
                    "Performance"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    # =========================================================
    # DOWNLOAD REPORT
    # =========================================================

    st.divider()

    csv = warehouse_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Warehouse Performance Report",
        data=csv,
        file_name="warehouse_performance_report.csv",
        mime="text/csv"
    )