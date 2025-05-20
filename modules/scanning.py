import streamlit as st
import socket

def pure_python_scan(target: str, ports=range(1, 1025), timeout=0.3):
    open_ports = []
    for port in ports:
        with socket.socket() as s:
            s.settimeout(timeout)
            try:
                s.connect((target, port))
                open_ports.append(port)
            except:
                pass
    return open_ports

def render():
    st.header("📡 Scanning (RGPD-safe, 100 % Python)")
    tab1, tab2 = st.tabs(["Port-scan Python","Web Scan"])

    # Onglet 1 : pure-Python scan
    with tab1:
        tgt = st.text_input("IP ou domaine", key="scan_tgt")
        # choix de ports personnalisés, ex. 22, 80, 443
        ports = st.text_input("Ports (comma-séparés)", "22,80,443")
        if st.button("Lancer scan", key="scan_btn") and tgt:
            # parser la liste de ports
            ports_list = [int(p.strip()) for p in ports.split(",") if p.strip().isdigit()]
            result = pure_python_scan(tgt, ports=ports_list)
            st.write(f"Ports ouverts sur {tgt} :", result)
            st.session_state.results.setdefault("scanning", {})[f"scan:{tgt}"] = result

    # Onglet 2 : Web Scan (ton code actuel)
    with tab2:
        url = st.text_input("URL pour Web Scan", key="scan_url")
        if st.button("Run Web Scan", key="scan_web_btn") and url:
            out = _nikto_like(url)  # comme avant ou fallback Python
            st.text(out)
            st.session_state.results.setdefault("scanning_web", {})[f"nikto:{url}"] = out
