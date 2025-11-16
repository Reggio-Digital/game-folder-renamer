import streamlit as st

# Import page modules
from pages_nav import setup, process, about

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

# Define pages for navigation
pages = {
    "Main": [
        st.Page(setup.show, title="Setup", icon="🔑"),
        st.Page(process.show, title="Scan & Process", icon="🎮"),
    ],
    "Information": [
        st.Page(about.show, title="About", icon="ℹ️"),
    ]
}

# Create navigation
pg = st.navigation(pages)

# Show connection status in sidebar
with st.sidebar:
    st.header("⚙️ Configuration Status")

    if st.session_state.igdb_client:
        st.success("✅ Connected to IGDB")
        if st.session_state.renamer:
            st.info(f"📁 Folder: {st.session_state.renamer.base_path}")
    else:
        st.warning("⚠️ Not connected")
        st.info("Configure in Setup page")

    st.divider()

    # Quick help
    with st.expander("ℹ️ Quick Guide"):
        st.markdown("""
        **Getting Started:**
        1. Get IGDB credentials from [Twitch](https://dev.twitch.tv/console)
        2. Enter credentials in **Setup** page
        3. Go to **Scan & Process** to rename folders
        4. Check **About** for more info
        """)

# Run the selected page
pg.run()
