import streamlit as st
import nmap

def _nmap_scan(target: str, args: str = "-sV -T4"):
    try:
        scanner = nmap.PortScanner()
        scanner.scan(target, arguments=args)
        return scanner[target]
    except Exception as e:
        return {"error": str(e)}

def render():
    st.header("📡 Scanning (Nmap via apt-get)")
    tab1, tab2 = st.tabs(["Nmap","Web Scan"])
    with tab1:
        tgt = st.text_input("IP ou CIDR", key="scan_tgt")
        if st.button("Run Nmap", key="scan_btn") and tgt:
            res = _nmap_scan(tgt)
            st.json(res)
            st.session_state.results.setdefault("scanning", {})[f"nmap:{tgt}"] = res
    # … ton code Web Scan …
