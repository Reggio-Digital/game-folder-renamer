import streamlit as st
import os
import yaml
from pathlib import Path
from game_renamer import IGDBClient, GameFolderRenamer

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

# Cached function to create and authenticate IGDB client
@st.cache_resource
def get_authenticated_igdb_client(client_id: str, client_secret: str):
    """Create and authenticate IGDB client with forever caching"""
    client = IGDBClient(client_id, client_secret)
    client.authenticate()
    return client

def show():
    """Display the Setup/Configuration page"""
    st.title("🔑 API Configuration")
    st.markdown("Configure your IGDB API credentials and games folder path")

    # Load saved configuration
    saved_config = load_config()

    # Get credentials from saved config or use defaults
    default_client_id = saved_config.get('client_id', '')
    default_client_secret = saved_config.get('client_secret', '')
    default_games_folder = saved_config.get('games_folder', os.path.expanduser('~'))

    # Show current connection status
    if st.session_state.get('igdb_client'):
        st.success("✅ Connected to IGDB")
        if st.session_state.get('renamer'):
            st.info(f"📁 Current folder: {st.session_state.renamer.base_path}")

        st.divider()

        # Show disconnect option
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔌 Disconnect and Reconfigure", use_container_width=True, type="secondary"):
                st.session_state.igdb_client = None
                st.session_state.renamer = None
                st.session_state.client_id = None
                st.session_state.client_secret = None
                st.session_state.folders = []
                st.session_state.processing_results = {}
                st.rerun()

        st.divider()
        st.info("💡 You're all set! Use the sidebar to navigate to 'Scan & Process' to start renaming your game folders.")
    else:
        # Configuration instructions
        st.divider()

        with st.expander("ℹ️ How to get your API credentials", expanded=True):
            st.markdown("""
            To use this app, you need to get free API credentials from IGDB (Internet Game Database).

            **Step-by-step guide:**
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
                    st.info("💡 Use the sidebar to navigate to 'Scan & Process' to start renaming your game folders.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Authentication failed: {str(e)}")
                    st.info("Please check your credentials and try again")
