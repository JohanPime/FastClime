import streamlit as st
import plotly.express as px
from fastclime.m4_dashboard.utils import read_duckdb

st.markdown("# 📈 Predictions")
st.sidebar.header("Predictions")

zone_id = st.text_input("Enter Zone ID", "panama_zone_a")

if zone_id:
    st.markdown(f"### Applied vs. Predicted Irrigation for Zone: `{zone_id}`")
    query = """
        SELECT d.ts, d.lamina_mm as applied, p.lamina_mm as predicted
        FROM deficit_proj d
        JOIN predictions p USING(ts)
        WHERE p.zone_id = ?
        ORDER BY d.ts
    """

    try:
        df = read_duckdb(query, (zone_id,))

        if not df.empty:
            fig = px.area(df, x="ts", y=["applied", "predicted"],
                          labels={"value": "Lámina (mm)", "variable": ""},
                          title="Applied vs Predicted Irrigation")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data found for Zone ID: {zone_id}")
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        st.warning("Please ensure the database at `~/.fastclime/data/catalog.db` contains the necessary tables (`deficit_proj`, `predictions`).")

else:
    st.info("Please enter a Zone ID to see the predictions.")
