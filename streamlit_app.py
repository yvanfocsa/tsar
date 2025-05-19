import streamlit as st
from modules import recon, scanning, exploit, osint, reporting, reverse_shell

# Page configuration
st.set_page_config(page_title="Pentest Toolbox", page_icon="🛠️", layout="wide")

# ---------------------------- AUTH (OIDC) ----------------------------
user = getattr(st, "user", None)

if not user or not getattr(user, "is_logged_in", False):

    # met tout dans le même conteneur pour garantir le centrage
    with st.container():
        st.markdown(
            """
            <style>
            /* Fond sobre */
            body, .stApp { background:#0f1e2b !important; }

            /* Bloc qui occupe 100 % de la hauteur et centre son contenu */
            .login-wrapper{
                height:100vh;
                display:flex;
                flex-direction:column;
                justify-content:center;   /* centrage vertical   */
                align-items:center;       /* centrage horizontal */
                text-align:center;
            }

            /* Bouton Streamlit (style léger) */
            .login-wrapper button{
                margin-top:1.5rem;
                font-size:1.05rem;
                padding:.6em 2.2em;
                border-radius:8px;
            }
            </style>

            <div class="login-wrapper">
                <h1>Pentest Toolbox – Connexion requise</h1>
                <p>Cette application est réservée aux utilisateurs autorisés.</p>
            """,
            unsafe_allow_html=True
        )

        # bouton centré (grâce au CSS ci-dessus)
        if st.button("Se connecter", type="secondary"):
            st.login()

        st.markdown("</div>", unsafe_allow_html=True)

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
