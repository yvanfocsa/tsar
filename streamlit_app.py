import streamlit as st
from modules import recon, scanning, exploit, osint, reporting, reverse_shell

# Page configuration
st.set_page_config(page_title="TSAR", page_icon="☢️", layout="wide")

# ---------------------------- AUTH (OIDC) ----------------------------
user = getattr(st, "user", None)
if not user or not getattr(user, "is_logged_in", False):
    # Centered full-screen login prompt
    st.markdown(
        """
        <style>
        .auth-container {
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background-color: #0f1e2b;
            color: #ffffff;
            margin: 0;
        }
        .auth-container button {
            margin-top: 1.5rem;
            font-size: 1.1rem;
            padding: 0.6em 2.2em;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.title("🔒 TSAR")
    st.write("Tactical Security Automation & Recon\nCliquez sur le bouton ci‑dessous pour vous connecter.")
    if st.button("Se connecter", type="primary"):
        st.login()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Déconnexion + profil dans la sidebar
with st.sidebar:
    st.markdown(f"👤 **{st.user.get('name', 'Utilisateur')}**")
    if st.button("Se déconnecter"):
        st.logout()

# ---------------------------- STATE INIT -----------------------------
def init_state():
    if "results" not in st.session_state:
        st.session_state.results = {}
init_state()

# ---------------------------- UI -------------------------------------
st.sidebar.image("assets/logo.png", width=290)
page = st.sidebar.radio(
    "Select module:",
    ["Dashboard", "Recon", "Scanning", "Exploit", "OSINT", "Reporting", "Reverse Shell"],
)

def _extract_target(key: str) -> str:
    return key.split(":", 1)[1] if ":" in key else key

if page == "Dashboard":
    st.markdown(
        "<div style='width:100%; text-align:center; margin:20px 0;'>"
        "<h1>Dashboard</h1>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center;'>"
        "Bienvenue sur le tableau de bord. Lancez un module pour voir les résultats ici."
        "</p>",
        unsafe_allow_html=True
    )
    if st.session_state.results:
        for section, items in st.session_state.results.items():
            if not items:
                continue
            for key, data in items.items():
                title = f"{section.capitalize()} – {_extract_target(key)}"
                with st.expander(title):
                    st.json(data) if data else st.warning("Pas de données.")
    else:
        st.info("Aucun résultat. Lancez un module.")

elif page == "Recon":
    recon.render()
elif page == "Scanning":
    scanning.render()
elif page == "Exploit":
    exploit.render()
elif page == "OSINT":
    osint.render()
elif page == "Reporting":
    reporting.render()
else:
    reverse_shell.render()

st.sidebar.info("💡 Sélectionnez un module pour commencer.")
