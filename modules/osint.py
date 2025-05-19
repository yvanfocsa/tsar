import streamlit as st
import requests

def _github(q: str): return requests.get(f"https://api.github.com/search/repositories?q={q}&per_page=5").json()

def render():
    st.header("🕵️ OSINT")
    [tab] = st.tabs(["GitHub"])
    with tab:
        q = st.text_input("Keyword", placeholder="cve-2025")
        if st.button("Search", key="osint_btn") and q:
            out = _github(q)
            st.session_state.results.setdefault("osint",{})[q] = out
            st.json(out)