import streamlit as st

# Import page modules
from pages_nav import home, setup, process

# Page configuration
st.set_page_config(
    page_title="Game Folder Renamer",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'igdb_client' not in st.session_state:
    st.session_state.igdb_client = None
if 'renamer' not in st.session_state:
    st.session_state.renamer = None
if 'folders' not in st.session_state:
    st.session_state.folders = []
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = {}
if 'pending_selections' not in st.session_state:
    st.session_state.pending_selections = {}
if 'client_id' not in st.session_state:
    st.session_state.client_id = None
if 'client_secret' not in st.session_state:
    st.session_state.client_secret = None
if 'dry_run' not in st.session_state:
    st.session_state.dry_run = False
if 'igdb_connection_failed' not in st.session_state:
    st.session_state.igdb_connection_failed = False

# Define pages for navigation
pages = [
    st.Page(home.show, title="Home", icon="🏠", url_path="home", default=True),
    st.Page(setup.show, title="Setup", icon="🔑", url_path="setup"),
    st.Page(process.show, title="Scan & Process", icon="🎮", url_path="process"),
]

# Create navigation
pg = st.navigation(pages)

# Show sidebar info
with st.sidebar:
    # Show connection status - check if credentials are saved OR client exists in session
    from pages_nav.setup import load_config
    saved_config = load_config()
    has_credentials = bool(saved_config.get('client_id') and saved_config.get('client_secret'))

    if st.session_state.get('igdb_connection_failed'):
        st.error("❌ Connection Failed")
    elif has_credentials or st.session_state.get('igdb_client') is not None:
        st.success("✅ Connected to IGDB")
    else:
        st.error("❌ Not Connected to IGDB")

    st.divider()

    # Show current folder if connected
    if st.session_state.get('renamer'):
        st.caption(f"📁 **Folder:**\n{st.session_state.renamer.base_path}")

    # GitHub link and credits at bottom
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; padding: 10px 0;'>
            <a href='https://github.com/Reggio-Digital/game-folder-renamer' target='_blank' style='text-decoration: none;'>
                <span style='font-size: 1.2em;'>⭐</span> View on GitHub
            </a>
        </div>
        <div style='text-align: center; padding: 5px 0; font-size: 0.9em;'>
            Made by <a href='https://reggiodigital.com' target='_blank' style='text-decoration: none;'>Reggio Digital</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# Run the selected page
pg.run()
