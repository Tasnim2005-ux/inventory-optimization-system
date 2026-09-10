import streamlit as st
import pandas as pd
import numpy as np


def show_abc_xyz_analysis(df):

    st.title("📦 ABC–XYZ Inventory Analysis")

    st.markdown(
        """
        This module classifies inventory based on:

        - **ABC Analysis:** Inventory value importance
        - **XYZ Analysis:** Demand variability
        - **ABC–XYZ Matrix:** Combined inventory segmentation
        """
    )

    st.divider()

    # =========================================================
    # ABC ANALYSIS
    # =========================================================

    st.header("📊 ABC Inventory Analysis")

    abc_data = (
        df.groupby("SKU_ID")
        .agg(
            Annual_Demand=("Units_Sold", "sum"),
            Unit_Cost=("Unit_Cost", "mean")
        )
        .reset_index()
    )

    # Annual consumption value

    abc_data["Annual_Consumption_Value"] = (
        abc_data["Annual_Demand"]
        * abc_data["Unit_Cost"]
    )

    # Sort by consumption value

    abc_data = (
        abc_data
        .sort_values(
            "Annual_Consumption_Value",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # Total value

    total_value = (
        abc_data["Annual_Consumption_Value"].sum()
    )

    # Value percentage

    if total_value > 0:

        abc_data["Value_Percentage"] = (
            abc_data["Annual_Consumption_Value"]
            / total_value
            * 100
        )

    else:

        abc_data["Value_Percentage"] = 0

    # Cumulative percentage

    abc_data["Cumulative_Percentage"] = (
        abc_data["Value_Percentage"]
        .cumsum()
    )

    # =========================================================
    # ABC CLASSIFICATION
    # =========================================================

    def classify_abc(cumulative_percentage):

        if cumulative_percentage <= 80:
            return "A"

        elif cumulative_percentage <= 95:
            return "B"

        else:
            return "C"

    abc_data["ABC_Class"] = (
        abc_data["Cumulative_Percentage"]
        .apply(classify_abc)
    )

    # =========================================================
    # ABC SUMMARY
    # =========================================================

    st.subheader("ABC Classification Summary")

    abc_summary = (
        abc_data.groupby("ABC_Class")
        .agg(
            SKUs=("SKU_ID", "count"),
            Consumption_Value=(
                "Annual_Consumption_Value",
                "sum"
            )
        )
        .reset_index()
    )

    abc_summary["Value_Share_%"] = (
        abc_summary["Consumption_Value"]
        / total_value
        * 100
        if total_value > 0
        else 0
    )

    st.dataframe(
        abc_summary,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("ABC Classification Details")

    st.dataframe(
        abc_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =========================================================
    # XYZ ANALYSIS
    # =========================================================

    st.header("📈 XYZ Demand Variability Analysis")

    xyz_data = (
        df.groupby(
            ["SKU_ID", "Warehouse_ID"]
        )
        .agg(
            Avg_Daily_Demand=(
                "Units_Sold",
                "mean"
            ),
            Demand_Std=(
                "Units_Sold",
                "std"
            )
        )
        .reset_index()
    )

    # Avoid NaN standard deviation

    xyz_data["Demand_Std"] = (
        xyz_data["Demand_Std"]
        .fillna(0)
    )

    # Coefficient of Variation

    xyz_data["Demand_CV"] = np.where(
        xyz_data["Avg_Daily_Demand"] > 0,
        xyz_data["Demand_Std"]
        / xyz_data["Avg_Daily_Demand"],
        0
    )

    # =========================================================
    # XYZ CLASSIFICATION
    # =========================================================

    def classify_xyz(cv):

        if cv <= 0.50:
            return "X"

        elif cv <= 1.00:
            return "Y"

        else:
            return "Z"

    xyz_data["XYZ_Class"] = (
        xyz_data["Demand_CV"]
        .apply(classify_xyz)
    )

    # =========================================================
    # XYZ SUMMARY
    # =========================================================

    st.subheader("XYZ Classification Summary")

    xyz_summary = (
        xyz_data.groupby("XYZ_Class")
        .agg(
            SKU_Warehouse_Combinations=(
                "SKU_ID",
                "count"
            ),
            Average_CV=(
                "Demand_CV",
                "mean"
            )
        )
        .reset_index()
    )

    st.dataframe(
        xyz_summary,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("XYZ Classification Details")

    st.dataframe(
        xyz_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =========================================================
    # ABC–XYZ MATRIX
    # =========================================================

    st.header("🎯 ABC–XYZ Inventory Matrix")

    # Merge ABC and XYZ

    matrix_df = xyz_data.merge(
        abc_data[
            [
                "SKU_ID",
                "ABC_Class"
            ]
        ],
        on="SKU_ID",
        how="left"
    )

    matrix_data = (
        matrix_df
        .groupby(
            [
                "ABC_Class",
                "XYZ_Class"
            ]
        )
        .size()
        .unstack(
            fill_value=0
        )
    )

    # Ensure A, B, C rows

    for abc_class in ["A", "B", "C"]:

        if abc_class not in matrix_data.index:

            matrix_data.loc[
                abc_class
            ] = 0

    # Ensure X, Y, Z columns

    for xyz_class in ["X", "Y", "Z"]:

        if xyz_class not in matrix_data.columns:

            matrix_data[xyz_class] = 0

    matrix_data = (
        matrix_data[
            ["X", "Y", "Z"]
        ]
        .sort_index()
    )

    st.dataframe(
        matrix_data,
        use_container_width=True
    )

    # =========================================================
    # MATRIX INTERPRETATION
    # =========================================================

    st.subheader("💡 Inventory Segmentation Interpretation")

    st.markdown(
        """
        | Segment | Meaning |
        |---|---|
        | **AX** | High-value, stable demand → Strong forecasting & tight control |
        | **AY** | High-value, moderately variable demand → Careful planning |
        | **AZ** | High-value, highly variable demand → Highest attention |
        | **BX** | Medium-value, stable demand → Standard control |
        | **BY** | Medium-value, moderate variability → Moderate monitoring |
        | **BZ** | Medium-value, highly variable demand → Risk monitoring |
        | **CX** | Low-value, stable demand → Simple replenishment |
        | **CY** | Low-value, moderate variability → Periodic review |
        | **CZ** | Low-value, highly variable demand → Flexible inventory policy |
        """
    )

    # =========================================================
    # KEY INSIGHT
    # =========================================================

    st.subheader("🔎 Key Inventory Insight")

    az_count = (
        matrix_df[
            (matrix_df["ABC_Class"] == "A")
            & (matrix_df["XYZ_Class"] == "Z")
        ]
        .shape[0]
    )

    st.info(
        f"⚠️ {az_count:,} SKU–warehouse combinations "
        "belong to the AZ category — high-value inventory "
        "with highly variable demand."
    )