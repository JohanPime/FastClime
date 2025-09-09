import streamlit as st
from fastapi import FastAPI
from streamlit.web import bootstrap
from fastclime.m4_dashboard.api.router import router as api_router

st.set_page_config(page_title="FastClime Dashboard", layout="wide")

# ---------- FastAPI ----------
api = FastAPI(title="FastClime API")
api.include_router(api_router, prefix="/api")

# Exponer instancia para uvicorn
app = api

# ---------- Streamlit ----------
def _run_streamlit() -> None:
    bootstrap.run("./src/fastclime/m4_dashboard/pages/1_Home.py")

if __name__ == "__main__":
    _run_streamlit()
