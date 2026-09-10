import streamlit as st


def show_home():

    st.title("📦 Inventory Optimization System")

    st.subheader(
        "A Data-Driven Decision Support System for Smarter Inventory Management"
    )

    st.write(
        "Analyze inventory, identify risks, optimize stock levels, "
        "and make better replenishment decisions through data-driven analytics."
    )

    st.divider()

    st.subheader("🔑 Key Features")

    st.markdown(
        """
        **ABC–XYZ Analysis** • **Safety Stock** • **Reorder Point (ROP)** •
        **EOQ** • **Inventory Risk** • **Supplier Performance** •
        **Warehouse Performance** • **Replenishment Optimization** •
        **Cost Optimization**
        """
    )

    st.divider()

    st.subheader("👨‍💻 Developed By")

    st.markdown(
        """
        ### Tasnim Bin Nasim

        **B.Sc. in Industrial & Production Engineering**  
        **Jashore University of Science and Technology (JUST)**

        *Aspiring Industrial Engineer focused on Data Analytics,
        Supply Chain Optimization & Intelligent Manufacturing Systems.*
        """
    )