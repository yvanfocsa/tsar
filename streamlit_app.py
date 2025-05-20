import streamlit as st
from streamlit_lottie import st_lottie
import requests
from modules import recon, scanning, exploit, osint, reporting, reverse_shell

# ——— Page configuration —————————————————————————————————————————
st.set_page_config(
    page_title="Pentest Toolbox",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ——— Helper pour charger un Lottie via URL —————————————————————————————————
def load_lottie(url: str):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return {}

# ——— AUTH (OIDC) —————————————————————————————————————————————————
user = getattr(st, "user", None)
if not user or not getattr(user, "is_logged_in", False):
    st.markdown(
        """
        <style>
        /* Fullscreen flexbox pour centrer */
        .login-container {
            height:100vh;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            background:#0f1e2b;
            color:white;
            text-align:center;
        }
        .login-container button {
            margin-top:1.5rem;
            font-size:1.1rem;
            padding:.6em 2.2em;
            border-radius:8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("🔒 Pentest Toolbox")
    st.write("Cette application est réservée aux utilisateurs autorisés.")
    if st.button("Se connecter", type="primary"):
        st.login()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ——— Sidebar : profil + déconnexion avec icône ——————————————————————————————
with st.sidebar:
    # Affiche nom d'utilisateur
    st.markdown(f"👤 **{st.user.get('name', 'Utilisateur')}**")
    # Disposition colonne pour icône et bouton
    col_icon, col_btn = st.columns([1, 6])
    with col_icon:
        st.image("assets/logout.png", width=24)
    with col_btn:
        if st.button("Se déconnecter"):
            st.logout()

# ——— Sidebar : style + logo animé + menu de modules —————————————————————————————————
st.sidebar.markdown(
    """
    <style>
    /* Sidebar dégradé */
    [data-testid="stSidebar"] > div:first-child {
      background: linear-gradient(180deg,#0f1e2b,#162a3a);
      padding:1rem;
    }
    /* Logo Lottie centré */
    .sidebar-logo {
      display:flex;
      justify-content:center;
      margin-bottom:1rem;
    }
    /* Menu modules stylé */
    .module-list { list-style:none; padding:0; margin:0; }
    .module-list li { margin:0.5rem 0; }
    .module-list li label {
      display:flex; align-items:center; cursor:pointer;
      padding:0.4rem 0.6rem; border-radius:6px;
      transition:background .2s;
    }
    .module-list li label:hover {
      background:rgba(255,255,255,0.05);
    }
    .module-list li input:checked + label {
      background:#ff4b4b; color:#fff;
    }
    .module-list li label span { margin-left:0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Chargement et affichage du logo animé
lottie_json = load_lottie("https://assets8.lottiefiles.com/packages/lf20_jcikwtux.json")
st.sidebar.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
st_lottie(lottie_json, height=100, key="side_logo")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Liste des modules
modules = ["Dashboard", "Recon", "Scanning", "Exploit", "OSINT", "Reporting", "Reverse Shell"]
# Radio pour synchronisation (caché)
current = st.sidebar.radio("", modules, index=0, label_visibility="collapsed")

# Menu HTML
st.sidebar.markdown("<ul class='module-list'>", unsafe_allow_html=True)
for idx, m in enumerate(modules):
    checked = "checked" if m == current else ""
    st.sidebar.markdown(
        f"""
        <li>
          <input type="radio" id="mod{idx}" name="mod" value="{m}" {checked}
                 onchange="window.location.search='?page={m}'" />
          <label for="mod{idx}"><span>{m}</span></label>
        </li>
        """,
        unsafe_allow_html=True,
    )
st.sidebar.markdown("</ul>", unsafe_allow_html=True)

# Synchronisation URL
query = st.experimental_get_query_params().get("page", [None])[0]
page = query if query in modules else current

# ——— STATE INIT ——————————————————————————————————————————————————————
def init_state():
    if "results" not in st.session_state:
        st.session_state.results = {}
init_state()

# ——— ROUTING PRINCIPALE —————————————————————————————————————————————————
def _extract_target(key: str) -> str:
    return key.split(":", 1)[1] if ":" in key else key

if page == "Dashboard":
    st.markdown("<h1 style='text-align:center;'>Dashboard</h1>", unsafe_allow_html=True)
    st.write("Bienvenue sur le tableau de bord. Lance un module pour voir les résultats ici.")
    if st.session_state.results:
        for section, items in st.session_state.results.items():
            if not items: continue
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
