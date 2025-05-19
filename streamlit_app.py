import streamlit as st
from modules import recon, scanning, exploit, osint, reporting, reverse_shell

# Page configuration
st.set_page_config(page_title="Pentest Toolbox", page_icon="🛠️", layout="wide")

# ---------------------------- AUTH (OIDC) ----------------------------
user = getattr(st, "user", None)

if not user or not getattr(user, "is_logged_in", False):
    # ► HTML + CSS pour centrer le contenu et ajouter un fond animé
    st.markdown(
        """
        <style>
        /* ---- CENTRAGE DU CONTENU ---- */
        .login-wrapper {
            position: relative;
            height: 100vh;             /* pleine hauteur */
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1;                /* au-dessus de la vague */
        }
        /* ---- BOUTON STREAMLIT ---- */
        button[kind="secondary"] {
            font-size: 18px;
            padding: 0.6em 2em;
            border-radius: 8px;
        }
        /* ---- FOND ANIMÉ (wave) ---- */
        .wave-bg {
            position: fixed;
            inset: 0;
            overflow: hidden;
            z-index: 0;                /* derrière le contenu */
        }
        .wave-bg > svg {
            position: absolute;
            width: 200%;
            height: 120%;
            top: 0;
            left: -50%;
            animation: drift 12s linear infinite;
            opacity: 0.15;             /* discrétion */
        }
        @keyframes drift {
            from { transform: translateX(0);   }
            to   { transform: translateX(-50%);}
        }
        </style>

        <div class="wave-bg">
            <!-- vague SVG -->
            <svg viewBox="0 0 1200 600" preserveAspectRatio="none">
                <path d="M0,300 C300,400 900,200 1200,300 L1200,600 L0,600 Z"
                      fill="#ffffff"></path>
            </svg>
        </div>

        <div class="login-wrapper">
            <h1>Pentest Toolbox – Connexion requise</h1>
            <p>Cette application est réservée aux utilisateurs autorisés.</p>
            """
        , unsafe_allow_html=True
    )

    # ► Bouton Streamlit “Se connecter”
    if st.button("Se connecter", type="secondary"):
        st.login()                # redirection Auth0 / OIDC

    st.markdown("</div>", unsafe_allow_html=True)  # ferme .login-wrapper
    st.stop()

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
