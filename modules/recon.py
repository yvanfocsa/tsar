import streamlit as st
import whois
import requests
from datetime import datetime

API_IPINFO = "https://ipinfo.io/{ip}/json"

def _whois_lookup(domain: str):
    try:
        return whois.whois(domain)
    except Exception as e:
        return {"error": str(e)}

def _ip_lookup(ip: str):
    try:
        resp = requests.get(API_IPINFO.format(ip=ip), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def render():
    st.header("🔍 Reconnaissance")
    tab1, tab2 = st.tabs(["WHOIS / Domain", "IP Lookup"])

    with tab1:
        domain = st.text_input("Domain", key="whois_domain", placeholder="example.com")
        if st.button("Run WHOIS", key="whois_btn") and domain:
            data = _whois_lookup(domain)
            st.session_state.results.setdefault("recon", {})[f"whois:{domain}"] = data
            st.json(data)

    with tab2:
        ip = st.text_input("IP address", key="whois_ip", placeholder="8.8.8.8")
        if st.button("Lookup IP", key="ip_btn") and ip:
            data = _ip_lookup(ip)
            st.session_state.results.setdefault("recon", {})[f"ip:{ip}"] = data
            st.json(data)

    st.caption(f"Last run: {datetime.utcnow():%Y-%m-%d %H:%M UTC}")
