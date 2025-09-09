import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠")

st.markdown("# FastClime Dashboard")
st.sidebar.header("Home")

st.write(
    """
    Welcome to the FastClime Dashboard.

    This interactive dashboard provides visualizations and insights from the FastClime toolkit.

    ### Modules:
    - **Datasets**: Explore the data catalog.
    - **Predictions**: View irrigation predictions.
    - **Water Balance**: Analyze the water balance components.

    Select a module from the sidebar to get started.
    """
)
