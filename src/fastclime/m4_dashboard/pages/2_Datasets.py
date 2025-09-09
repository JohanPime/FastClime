import streamlit as st
import plotly.express as px
from fastclime.m4_dashboard.utils import load_dataset_summary

st.markdown("# 📂 Data Catalog")
df = load_dataset_summary()

st.dataframe(df, use_container_width=True)

fig = px.bar(df, x="dataset", y="files", title="Files per dataset")
st.plotly_chart(fig, use_container_width=True)
