import streamlit as st
import pandas as pd


def show_supplier_performance(df):

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("🚚 Supplier Performance")

    st.markdown(
        """
        Evaluate supplier performance based on **order volume,
        lead time, cost, stockout rate, and overall reliability**.
        """
    )

    st.divider()

    # =========================================================
    # REQUIRED COLUMNS CHECK
    # =========================================================

    required_columns = [
        "Supplier_ID",
        "Supplier_Lead_Time_Days",
        "Unit_Cost",
        "Units_Ordered",
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
    # SUPPLIER PERFORMANCE DATA
    # =========================================================

    supplier_df = (
        df.groupby("Supplier_ID", as_index=False)
        .agg(
            Orders=("Supplier_ID", "size"),
            Units_Ordered=("Units_Ordered", "sum"),
            Avg_Lead_Time=("Supplier_Lead_Time_Days", "mean"),
            Avg_Unit_Cost=("Unit_Cost", "mean"),
            Stockouts=("Stockout_Flag", "sum")
        )
    )

    # =========================================================
    # PERFORMANCE METRICS
    # =========================================================

    supplier_df["Stockout_Rate"] = (
        supplier_df["Stockouts"]
        / supplier_df["Orders"]
        * 100
    )

    # =========================================================
    # SUPPLIER RANK
    # =========================================================

    supplier_df["Supplier_Score"] = (
        supplier_df["Stockout_Rate"].rank(
            ascending=True,
            pct=True
        ) * 50
        +
        supplier_df["Avg_Lead_Time"].rank(
            ascending=True,
            pct=True
        ) * 30
        +
        supplier_df["Avg_Unit_Cost"].rank(
            ascending=True,
            pct=True
        ) * 20
    )

    supplier_df["Supplier_Rank"] = (
        supplier_df["Supplier_Score"]
        .rank(ascending=True)
        .astype(int)
    )

    # =========================================================
    # PERFORMANCE CATEGORY
    # =========================================================

    supplier_df["Performance"] = pd.cut(
        supplier_df["Supplier_Rank"],
        bins=[
            0,
            max(1, len(supplier_df) * 0.25),
            max(2, len(supplier_df) * 0.50),
            max(3, len(supplier_df) * 0.75),
            len(supplier_df)
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

    st.subheader("📊 Supplier Performance Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Suppliers",
            f"{supplier_df['Supplier_ID'].nunique():,}"
        )

    with col2:
        st.metric(
            "Total Orders",
            f"{supplier_df['Orders'].sum():,}"
        )

    with col3:
        st.metric(
            "Avg Lead Time",
            f"{supplier_df['Avg_Lead_Time'].mean():.1f} days"
        )

    with col4:
        st.metric(
            "Overall Stockout Rate",
            f"{supplier_df['Stockout_Rate'].mean():.2f}%"
        )

    st.divider()

    # =========================================================
    # SUPPLIER TABLE
    # =========================================================

    st.subheader("🚚 Supplier Performance Scorecard")

    display_columns = [
        "Supplier_ID",
        "Orders",
        "Units_Ordered",
        "Avg_Lead_Time",
        "Avg_Unit_Cost",
        "Stockouts",
        "Stockout_Rate",
        "Supplier_Rank",
        "Performance"
    ]

    display_df = supplier_df[display_columns].sort_values(
        "Supplier_Rank"
    )

    st.dataframe(
        display_df.style.format({
            "Orders": "{:,.0f}",
            "Units_Ordered": "{:,.0f}",
            "Avg_Lead_Time": "{:.2f}",
            "Avg_Unit_Cost": "${:.2f}",
            "Stockouts": "{:,.0f}",
            "Stockout_Rate": "{:.2f}%",
            "Supplier_Rank": "{:,.0f}"
        }),
        use_container_width=True
    )

    # =========================================================
    # CHARTS
    # =========================================================

    st.divider()

    st.subheader("📈 Supplier Analysis")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Average Lead Time")

        lead_time_chart = (
            supplier_df
            .sort_values("Avg_Lead_Time", ascending=False)
            .set_index("Supplier_ID")[
                "Avg_Lead_Time"
            ]
        )

        st.bar_chart(lead_time_chart)

    with col2:

        st.markdown("### Stockout Rate")

        stockout_chart = (
            supplier_df
            .sort_values("Stockout_Rate", ascending=False)
            .set_index("Supplier_ID")[
                "Stockout_Rate"
            ]
        )

        st.bar_chart(stockout_chart)

    # =========================================================
    # TOP / WORST SUPPLIERS
    # =========================================================

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🏆 Top Suppliers")

        top_suppliers = (
            supplier_df
            .sort_values("Supplier_Rank")
            .head(5)
        )

        st.dataframe(
            top_suppliers[
                [
                    "Supplier_ID",
                    "Avg_Lead_Time",
                    "Stockout_Rate",
                    "Supplier_Rank",
                    "Performance"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    with col2:

        st.subheader("⚠️ Suppliers Needing Attention")

        weak_suppliers = (
            supplier_df
            .sort_values("Supplier_Rank", ascending=False)
            .head(5)
        )

        st.dataframe(
            weak_suppliers[
                [
                    "Supplier_ID",
                    "Avg_Lead_Time",
                    "Stockout_Rate",
                    "Supplier_Rank",
                    "Performance"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    # =========================================================
    # DOWNLOAD
    # =========================================================

    st.divider()

    csv = supplier_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Supplier Performance Report",
        data=csv,
        file_name="supplier_performance_report.csv",
        mime="text/csv"
    )