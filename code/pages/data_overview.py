import streamlit as st
import pandas as pd


def show_data_overview(df):

    st.title("📊 Data Overview")

    st.write("Dataset overview and basic information")

    st.divider()

    st.subheader("📌 Dataset Size")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Records", f"{df.shape[0]:,}")

    with col2:
        st.metric("Total Variables", f"{df.shape[1]:,}")
    st.divider()
    st.subheader("🔗 Supply Chain Entities")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Unique SKUs", f"{df['SKU_ID'].nunique():,}")

    with col2:
        st.metric("Warehouses", f"{df['Warehouse_ID'].nunique():,}")

    with col3:
        st.metric("Suppliers", f"{df['Supplier_ID'].nunique():,}")

    with col4:
        st.metric("Regions", f"{df['Region'].nunique():,}")                