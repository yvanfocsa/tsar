import streamlit as st
import subprocess, os

def _nmap_scan(target: str, args: str = "-sV -T4"):
    # On force le binaire exécutable
    os.chmod("assets/bin/nmap", 0o755)

    # On pointe datadir sur notre dossier nmap-data
    data_dir = os.path.join(os.getcwd(), "assets", "share", "nmap-data")
    cmd = f"./assets/bin/nmap --datadir {data_dir} {args} {target}"
    try:
        return subprocess.check_output(cmd, shell=True,
                                       text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output

def render():
    st.header("📡 Scanning (Nmap statique)")
    tgt = st.text_input("IP ou CIDR", key="scan_tgt")
    if st.button("Run Nmap", key="scan_btn") and tgt:
        out = _nmap_scan(tgt)
        st.code(out, language="text")
        st.session_state.results.setdefault("scanning", {})[f"nmap:{tgt}"] = out
