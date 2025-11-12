import streamlit as st
import os
import yaml
from pathlib import Path
from game_renamer import IGDBClient, GameFolderRenamer

# Page configuration
st.set_page_config(
    page_title="Game Folder Renamer",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cached function to create and authenticate IGDB client
@st.cache_resource
def get_authenticated_igdb_client(client_id: str, client_secret: str):
    """Create and authenticate IGDB client with forever caching"""
    client = IGDBClient(client_id, client_secret)
    client.authenticate()
    return client

# Cached function for game searches
@st.cache_data(ttl=None)  # ttl=None means cache forever
def search_game_cached(client_id: str, client_secret: str, game_name: str):
    """Search for a game with forever caching"""
    client = get_authenticated_igdb_client(client_id, client_secret)
    return client.search_game(game_name)

# Configuration file management
CONFIG_FILE = Path.home() / '.game_renamer_config.yaml'

def load_config():
    """Load configuration from YAML file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    return {}

def save_config(config):
    """Save configuration to YAML file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        st.error(f"Failed to save config: {str(e)}")
        return False

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

# Load saved configuration
saved_config = load_config()

# Get credentials from saved config or use defaults
default_client_id = saved_config.get('client_id', '')
default_client_secret = saved_config.get('client_secret', '')
default_games_folder = saved_config.get('games_folder', os.path.expanduser('~'))

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Show connection status
    if st.session_state.igdb_client:
        st.success("✅ Connected to IGDB")
        if st.session_state.renamer:
            st.info(f"📁 Folder: {st.session_state.renamer.base_path}")

        # Disconnect button
        if st.button("🔌 Disconnect", use_container_width=True):
            st.session_state.igdb_client = None
            st.session_state.renamer = None
            st.session_state.client_id = None
            st.session_state.client_secret = None
            st.session_state.folders = []
            st.session_state.processing_results = {}
            st.rerun()
    else:
        st.warning("⚠️ Not connected")
        st.info("Enter your API credentials in the main area to get started")

    st.divider()

    # Instructions
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. Get your IGDB credentials from [Twitch Developer Console](https://dev.twitch.tv/console)
        2. Enter your Client ID and Client Secret in the app
        3. Specify the path to your games folder
        4. Click 'Connect to IGDB'
        5. Click 'Scan Folders' to see all game folders
        6. Process folders to rename them
        """)

# Main content area
st.title("🎮 Game Folder Renamer")
st.markdown("Automatically rename your game folders using the IGDB database")

# Show configuration screen if not connected
if not st.session_state.igdb_client:
    st.divider()

    # Configuration instructions
    st.subheader("🔑 API Configuration Required")
    st.markdown("""
    To use this app, you need to get free API credentials from IGDB (Internet Game Database).

    **How to get your API credentials:**
    1. Go to the [Twitch Developer Console](https://dev.twitch.tv/console/apps)
    2. Log in with your Twitch account (create one if needed - it's free)
    3. Click "Register Your Application"
    4. Fill in the form:
       - **Name**: Game Folder Renamer (or any name you like)
       - **OAuth Redirect URLs**: http://localhost
       - **Category**: Application Integration
    5. Click "Create" and then "Manage"
    6. Copy your **Client ID** and **Client Secret**
    7. Enter them below and click "Connect to IGDB"
    """)

    st.divider()

    # Configuration form
    with st.form("setup_form"):
        st.write("### Enter Your Credentials")

        client_id = st.text_input(
            "IGDB Client ID",
            value=default_client_id,
            type="password",
            placeholder="Enter your Client ID from Twitch Developer Console",
            help="Your Client ID from Twitch Developer Console"
        )

        client_secret = st.text_input(
            "IGDB Client Secret",
            value=default_client_secret,
            type="password",
            placeholder="Enter your Client Secret from Twitch Developer Console",
            help="Your Client Secret from Twitch Developer Console"
        )

        st.write("### Specify Games Folder")

        games_folder = st.text_input(
            "Games Folder Path",
            value=default_games_folder,
            placeholder="e.g., /home/user/games or C:\\Games",
            help="Full path to the folder containing your game folders"
        )

        # Save settings option
        save_settings = st.checkbox(
            "Save these settings for next time",
            value=True,
            help="Settings will be saved to ~/.game_renamer_config.yaml"
        )

        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🔌 Connect to IGDB", use_container_width=True, type="primary")

    # Handle form submission
    if submitted:
        if not client_id or not client_secret:
            st.error("❌ Please provide both Client ID and Client Secret")
        elif not games_folder:
            st.error("❌ Please provide a games folder path")
        elif not os.path.exists(games_folder):
            st.error(f"❌ Games folder does not exist: {games_folder}")
        else:
            try:
                with st.spinner("🔄 Authenticating with IGDB..."):
                    # Use cached authentication
                    igdb_client = get_authenticated_igdb_client(client_id, client_secret)
                    st.session_state.igdb_client = igdb_client
                    st.session_state.renamer = GameFolderRenamer(igdb_client, games_folder)
                    st.session_state.client_id = client_id
                    st.session_state.client_secret = client_secret

                    # Save settings if requested
                    if save_settings:
                        config = {
                            'client_id': client_id,
                            'client_secret': client_secret,
                            'games_folder': games_folder
                        }
                        save_config(config)

                st.success("✅ Connected successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Authentication failed: {str(e)}")
                st.info("Please check your credentials and try again")

    st.stop()

# Action buttons
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    if st.button("🔍 Scan Folders", use_container_width=True):
        with st.spinner("Scanning folders..."):
            folders = st.session_state.renamer.get_folders()
            if isinstance(folders, dict) and 'error' in folders:
                st.error(f"Error scanning folders: {folders['error']}")
            else:
                st.session_state.folders = folders
                st.session_state.processing_results = {}
                st.session_state.pending_selections = {}
                st.rerun()

with col2:
    if st.button("🔄 Process All Folders", use_container_width=True, disabled=len(st.session_state.folders) == 0):
        st.session_state.processing_mode = True

with col3:
    if st.button("🗑️ Clear Results", use_container_width=True):
        st.session_state.processing_results = {}
        st.session_state.pending_selections = {}
        st.rerun()

# Show statistics
if st.session_state.folders:
    st.divider()

    total_folders = len(st.session_state.folders)
    already_named = sum(1 for f in st.session_state.folders if f['already_named'])
    to_process = total_folders - already_named

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric("Total Folders", total_folders)
    with stat_col2:
        st.metric("Already Named", already_named)
    with stat_col3:
        st.metric("To Process", to_process)
    with stat_col4:
        processed = len(st.session_state.processing_results)
        st.metric("Processed", processed)

    st.divider()

# Process folders if in processing mode
if st.session_state.folders and 'processing_mode' in st.session_state and st.session_state.processing_mode:
    st.session_state.processing_mode = False

    progress_bar = st.progress(0)
    status_text = st.empty()

    folders_to_process = [f for f in st.session_state.folders if not f['already_named']]
    total = len(folders_to_process)

    for idx, folder in enumerate(folders_to_process):
        folder_name = folder['name']

        # Skip if already processed
        if folder_name in st.session_state.processing_results:
            continue

        status_text.text(f"Processing {idx + 1}/{total}: {folder_name}")
        progress_bar.progress((idx + 1) / total)

        # Search for game using cached function
        result = search_game_cached(
            st.session_state.client_id,
            st.session_state.client_secret,
            folder_name
        )
        st.session_state.processing_results[folder_name] = result

    status_text.text("Processing complete!")
    st.rerun()

# Display results
if st.session_state.processing_results:
    st.subheader("📊 Processing Results")

    # Group results by status
    single_matches = []
    multiple_matches = []
    not_found = []
    errors = []
    renamed = []

    for folder_name, result in st.session_state.processing_results.items():
        if isinstance(result, dict):
            if result.get('status') == 'single_match':
                single_matches.append((folder_name, result))
            elif result.get('status') == 'multiple_matches':
                multiple_matches.append((folder_name, result))
            elif result.get('status') == 'not_found':
                not_found.append(folder_name)
            elif result.get('status') == 'error':
                errors.append(folder_name)
            elif result.get('status') == 'renamed':
                renamed.append((folder_name, result))

    # Create tabs for different result types
    tab1, tab2, tab3, tab4 = st.tabs([
        f"✅ Auto-Renamed ({len(single_matches)})",
        f"🤔 Needs Selection ({len(multiple_matches)})",
        f"❌ Not Found ({len(not_found)})",
        f"⚠️ Errors ({len(errors)})"
    ])

    with tab1:
        if single_matches:
            for folder_name, result in single_matches:
                game = result['game']
                year_str = f" ({game['year']})" if game['year'] != "TBA" else ""
                new_name = f"{game['name']}{year_str}"
                remake_badge = " 🔄 (Remake/Remaster)" if game['is_remake'] else ""

                with st.expander(f"📁 {folder_name} → {new_name}{remake_badge}"):
                    st.write(f"**Original:** {folder_name}")
                    st.write(f"**New Name:** {new_name}")
                    st.write(f"**Year:** {game['year']}")
                    if game['is_remake']:
                        st.info("This is a remake or remaster")

                    if st.button(f"✅ Rename", key=f"rename_{folder_name}"):
                        with st.spinner(f"Renaming {folder_name}..."):
                            rename_result = st.session_state.renamer.rename_folder(folder_name, new_name)
                            if rename_result['success']:
                                st.success(f"Renamed to: {new_name}")
                                result['status'] = 'renamed'
                                st.rerun()
                            else:
                                st.error(f"Error: {rename_result['error']}")
        else:
            st.info("No single matches found")

    with tab2:
        if multiple_matches:
            for folder_name, result in multiple_matches:
                with st.expander(f"📁 {folder_name}"):
                    st.write(f"**Original Folder:** {folder_name}")
                    st.write(f"**Search Query:** {result['query']}")
                    st.write("**Select the correct game:**")

                    games = result['games']
                    options = []
                    for i, game in enumerate(games):
                        year_str = f" ({game['year']})" if game['year'] != "TBA" else ""
                        remake_str = " [Remake/Remaster]" if game['is_remake'] else ""
                        options.append(f"{game['name']}{year_str}{remake_str}")

                    options.append("❌ Skip this folder")

                    selected = st.selectbox(
                        "Choose a game:",
                        options,
                        key=f"select_{folder_name}"
                    )

                    col_btn1, col_btn2 = st.columns([1, 5])
                    with col_btn1:
                        if st.button("✅ Apply", key=f"apply_{folder_name}"):
                            if selected == "❌ Skip this folder":
                                st.info("Skipped")
                            else:
                                # Find selected game
                                selected_idx = options.index(selected)
                                if selected_idx < len(games):
                                    selected_game = games[selected_idx]
                                    year_str = f" ({selected_game['year']})" if selected_game['year'] != "TBA" else ""
                                    new_name = f"{selected_game['name']}{year_str}"

                                    with st.spinner(f"Renaming {folder_name}..."):
                                        rename_result = st.session_state.renamer.rename_folder(folder_name, new_name)
                                        if rename_result['success']:
                                            st.success(f"Renamed to: {new_name}")
                                            result['status'] = 'renamed'
                                            st.rerun()
                                        else:
                                            st.error(f"Error: {rename_result['error']}")
        else:
            st.info("No folders with multiple matches")

    with tab3:
        if not_found:
            st.warning("The following folders could not be found in IGDB:")
            for folder_name in not_found:
                st.text(f"• {folder_name}")
        else:
            st.info("All folders were found in IGDB")

    with tab4:
        if errors:
            st.error("The following folders had errors:")
            for folder_name in errors:
                st.text(f"• {folder_name}")
        else:
            st.info("No errors occurred")

# Show folder list if scanned
elif st.session_state.folders:
    st.subheader("📁 Scanned Folders")

    for folder in st.session_state.folders:
        if folder['already_named']:
            st.success(f"✅ {folder['name']} (already properly named)")
        else:
            st.info(f"📁 {folder['name']}")
