import streamlit as st

# Import page modules
from pages_nav import home, setup, process, about

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

# Define pages for navigation
pages = [
    st.Page(home.show, title="Home", icon="🏠", url_path="home", default=True),
    st.Page(setup.show, title="Setup", icon="🔑", url_path="setup"),
    st.Page(process.show, title="Scan & Process", icon="🎮", url_path="process"),
    st.Page(about.show, title="About", icon="ℹ️", url_path="about"),
]

# Create navigation
pg = st.navigation(pages)

# Show progress indicator in sidebar
with st.sidebar:
    st.header("📋 Progress")

    # Calculate progress steps
    is_connected = st.session_state.get('igdb_client') is not None
    has_folders = len(st.session_state.get('folders', [])) > 0
    has_results = len(st.session_state.get('processing_results', {})) > 0

    # Step 1: Connect
    if is_connected:
        st.success("✅ Step 1: Connected to IGDB")
    else:
        st.warning("⏳ Step 1: Connect to IGDB")

    # Step 2: Scan
    if has_folders:
        st.success(f"✅ Step 2: Scanned ({len(st.session_state.folders)} folders)")
    else:
        if is_connected:
            st.info("⏳ Step 2: Scan your folders")
        else:
            st.text("⏸️ Step 2: Scan your folders")

    # Step 3: Process
    if has_results:
        st.success(f"✅ Step 3: Processed ({len(st.session_state.processing_results)} results)")
    else:
        if has_folders:
            st.info("⏳ Step 3: Process folders")
        else:
            st.text("⏸️ Step 3: Process folders")

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
