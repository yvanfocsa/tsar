import streamlit as st
import subprocess
import os

def _nmap_scan(target: str, args: str = "-sV -T4"):
    # 1) chmod pour être sûr, même si Git Windows n'a pas propagé le bit
    os.chmod("assets/bin/nmap", 0o755)

    # 2) appel du binaire statique
    cmd = f"./assets/bin/nmap {args} {target}"
    try:
        output = subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.STDOUT
        )
        return output
    except subprocess.CalledProcessError as e:
        return e.output

def render():
    st.header("📡 Scanning (Nmap statique)")
    target = st.text_input("IP ou CIDR", key="scan_tgt")
    if st.button("Run Nmap", key="scan_btn") and target:
        out = _nmap_scan(target)
        st.code(out, language="text")
        st.session_state.results.setdefault("scanning", {})[f"nmap:{target}"] = out
