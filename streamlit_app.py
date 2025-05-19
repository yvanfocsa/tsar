import streamlit as st
from modules import recon, scanning, exploit, osint, reporting, reverse_shell

# Page configuration
st.set_page_config(page_title="Pentest Toolbox", page_icon="🛠️", layout="wide")

# ---------------------------- AUTH (OIDC) ----------------------------
user = getattr(st, "user", None)

if not user or not getattr(user, "is_logged_in", False):

    with st.container():
        st.markdown(
            """
            <style>
            /* --- thème sombre arrière-plan --- */
            body, .stApp { background:#123 !important; overflow:hidden; }

            /* --- bloc centré verticalement & horizontalement --- */
            .login-wrapper{
                height:100vh;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                text-align:center;
                z-index:1;
            }

            /* ➜ centre le bouton Streamlit ET son conteneur */
            .login-wrapper button {
                margin:0 auto;             /* centre horizontalement */
                display:block;              /* bouton = bloc centré */
                font-size:1.1rem;
                padding:.6em 2.5em;
                border-radius:10px;
            }

            /* --- décor animé "dots" --- */
            .dot-field::before,
            .dot-field::after{
                position:fixed;
                top:50%; left:50%;
                width:3em; height:3em;
                content:'.';
                font-size:52px;
                color:transparent;
                mix-blend-mode:screen;
                animation:move 44s ease-in-out infinite alternate;
                text-shadow:
                    2.3em 1.8em 7px hsla(12 ,100%,50%,.9),
                   -1.8em -.6em 7px hsla(204,100%,50%,.9),
                    .2em -2.2em 7px hsla(320,100%,50%,.9),
                   -2.6em 2em 7px hsla(265,100%,50%,.9),
                    1.5em 2.5em 7px hsla(44 ,100%,50%,.9),
                   -2.9em -1.3em 7px hsla(175,100%,50%,.9),
                    2.7em -1.8em 7px hsla(300,100%,50%,.9),
                   -.4em 2.9em 7px hsla(110,100%,50%,.9),
                    .9em -2.9em 7px hsla(80 ,100%,50%,.9),
                   -2.8em .4em 7px hsla(230,100%,50%,.9),
                    2.9em .7em 7px hsla(350,100%,50%,.9),
                   -1em 2.7em 7px hsla(60 ,100%,50%,.9),
                   -2.4em -2.3em 7px hsla(190,100%,50%,.9),
                    2em -2.4em 7px hsla(280,100%,50%,.9),
                   -.7em 2em 7px hsla(30 ,100%,50%,.9),
                   -1.3em -2.8em 7px hsla(140,100%,50%,.9);
            }
            .dot-field::after{
                animation-duration:41s;
                animation-delay:-18s;
                transform:scale(1.25);
            }
            @keyframes move{
                from{ transform:rotate(0deg)   scale(12) translateX(-20px); }
                to  { transform:rotate(360deg) scale(18) translateX( 20px); }
            }
            </style>

            <!-- décor animé -->
            <div class="dot-field"></div>

            <!-- contenu principal -->
            <div class="login-wrapper">
                <h1>Pentest Toolbox – Connexion requise</h1>
                <p>Cette application est réservée aux utilisateurs autorisés.</p>
            """,
            unsafe_allow_html=True
        )

        # Bouton centré grâce au CSS ci-dessus
        if st.button("Se connecter", type="secondary"):
            st.login()

        st.markdown("</div>", unsafe_allow_html=True)   # ferme .login-wrapper

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
