import streamlit as st
from fpdf import FPDF
from io import BytesIO
import json, datetime

class _PDF(FPDF):
    def header(self):
        self.set_font("Helvetica","B",16)
        self.cell(0,10,"Report",ln=True,align="C")
        self.ln(8)

def _generate_pdf(data: dict):
    pdf = _PDF()
    pdf.add_page()
    # Set base font for content
    pdf.set_font("Courier", size=10)
    for sec, itm in data.items():
        # Section header in bold
        pdf.set_font("Courier", style="B", size=10)
        pdf.cell(0, 8, f"[{sec.upper()}]", ln=True)
        # Reset to regular font
        pdf.set_font("Courier", size=10)
        # Dump JSON content
        pdf.multi_cell(0, 5, json.dumps(itm, indent=2, default=str))
        pdf.ln(4)
    buf = BytesIO()
    pdf.output(buf)
    return buf

def render():
    st.header("📝 Reporting")
    t1, t2 = st.tabs(["View Data","Generate PDF"])
    with t1:
        if not st.session_state.results: st.info("No data yet.")
        else: st.json(st.session_state.results)
    with t2:
        if not st.session_state.results: st.warning("No data yet.")
        elif st.button("Generate PDF",key="rep_btn"):
            buf = _generate_pdf(st.session_state.results)
            fn = datetime.datetime.utcnow().strftime("report_%Y%m%d_%H%M.pdf")
            st.download_button("Download PDF", buf.getvalue(), file_name=fn, mime="application/pdf")
