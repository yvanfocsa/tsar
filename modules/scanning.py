import streamlit as st
import nmap
import subprocess
import shlex

def _nmap_scan(target: str, args: str = "-sV -T4"):
    try:
        scanner = nmap.PortScanner()
        scanner.scan(target, arguments=args)
        return scanner[target]
    except Exception as e:
        return {"error": str(e)}


def _nikto_like(url: str):
    """
    Run a Nikto-like web scan and return combined stdout and stderr.
    """
    cmd = f"nikto -host {shlex.quote(url)}"
    try:
        result = subprocess.run(
            cmd, shell=True, text=True, capture_output=True, timeout=120
        )
        output = result.stdout.strip() if result.stdout else ""
        error  = result.stderr.strip() if result.stderr else ""
        # Combine stdout and stderr with an explicit "\n"
        return (output + "\n" + error).strip()
    except subprocess.TimeoutExpired as e:
        return f"Scan timed out after {e.timeout} seconds"
    except Exception as e:
        return str(e)


def render():
    st.header("📡 Scanning")
    tab1, tab2 = st.tabs(["Nmap", "Web Scan"])

    with tab1:
        target = st.text_input("IP or CIDR", key="scan_tgt")
        if st.button("Run Nmap", key="scan_btn") and target:
            result = _nmap_scan(target)
            st.session_state.results.setdefault("scanning", {})[f"nmap:{target}"] = result
            st.json(result)

    with tab2:
        url = st.text_input("URL for web scan", key="scan_url")
        if st.button("Run Web Scan", key="scan_web_btn") and url:
            out = _nikto_like(url)
            st.session_state.results.setdefault("scanning_web", {})[f"nikto:{url}"] = out
            st.text(out)
