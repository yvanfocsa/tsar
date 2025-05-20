import streamlit as st
import requests

def nmap_api_scan(target: str):
    url = f"https://api.hackertarget.com/nmap/?q={target}"
    resp = requests.get(url, timeout=60)
    return resp.text if resp.ok else f"Erreur API {resp.status_code}"

def render():
    st.header("📡 Scanning")
    tab1, tab2 = st.tabs(["Nmap API","Web Scan"])

    with tab1:
        tgt = st.text_input("IP ou domaine", key="scan_tgt")
        if st.button("Lancer Nmap API", key="scan_btn") and tgt:
            out = nmap_api_scan(tgt)
            st.code(out, language="text")
            st.session_state.results.setdefault("scanning", {})[f"nmap:{tgt}"] = out

    with tab2:
        # votre code Web Scan actuel
        url = st.text_input("URL pour Web Scan", key="scan_url")
        if st.button("Run Web Scan", key="scan_web_btn") and url:
            out = nikto_like(url)  # ou pure-Python fallback
            st.text(out)
            st.session_state.results.setdefault("scanning_web", {})[f"nikto:{url}"] = out
