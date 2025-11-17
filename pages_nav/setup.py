import streamlit as st
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from game_renamer import IGDBClient, GameFolderRenamer

# Configuration file management
CONFIG_FILE = Path.home() / '.game_renamer_config.yaml'


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file

    Returns:
        Configuration dictionary, or empty dict if file doesn't exist or is invalid
    """
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f)
                return config if config else {}
        except yaml.YAMLError as e:
            st.warning(f"⚠️ Config file corrupted, ignoring: {str(e)}")
            return {}
        except OSError as e:
            st.warning(f"⚠️ Could not read config file: {str(e)}")
            return {}
    return {}


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to YAML file

    Args:
        config: Configuration dictionary to save

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(CONFIG_FILE, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)
        return True
    except OSError as e:
        st.error(f"❌ Failed to save config: {str(e)}")
        return False
    except yaml.YAMLError as e:
        st.error(f"❌ Failed to serialize config: {str(e)}")
        return False


@st.cache_resource
def get_authenticated_igdb_client(client_id: str, client_secret: str) -> IGDBClient:
    """Create and authenticate IGDB client with forever caching

    Args:
        client_id: IGDB client ID
        client_secret: IGDB client secret

    Returns:
        Authenticated IGDBClient instance

    Raises:
        Exception: If authentication fails
    """
    client = IGDBClient(client_id, client_secret)
    client.authenticate()
    return client


def _validate_credentials(client_id: str, client_secret: str, games_folder: str) -> Optional[str]:
    """Validate user input credentials and folder path

    Args:
        client_id: IGDB client ID
        client_secret: IGDB client secret
        games_folder: Path to games folder

    Returns:
        Error message if validation fails, None otherwise
    """
    if not client_id or not client_secret:
        return "Please provide both Client ID and Client Secret"

    if not games_folder:
        return "Please provide a games folder path"

    # Expand user path if needed
    expanded_path = os.path.expanduser(games_folder)

    if not os.path.exists(expanded_path):
        return f"Games folder does not exist: {expanded_path}"

    if not os.path.isdir(expanded_path):
        return f"Path is not a directory: {expanded_path}"

    # Check if we have read permissions
    if not os.access(expanded_path, os.R_OK):
        return f"No read permission for folder: {expanded_path}"

    return None


def _render_disconnect_section() -> None:
    """Render the disconnect and reconfigure section when already connected"""
    st.success("✅ Connected to IGDB")

    if st.session_state.get('renamer'):
        st.info(f"📁 Current folder: {st.session_state.renamer.base_path}")

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔌 Disconnect and Reconfigure", use_container_width=True, type="secondary"):
            _handle_disconnect()

    st.divider()
    st.success("🎉 **You're all set!**")
    st.info("👉 Go to **Home** to see your next steps, or jump straight to **Scan & Process** to start renaming!")


def _handle_disconnect() -> None:
    """Handle disconnecting and clearing session state"""
    st.session_state.igdb_client = None
    st.session_state.renamer = None
    st.session_state.client_id = None
    st.session_state.client_secret = None
    st.session_state.folders = []
    st.session_state.processing_results = {}
    st.rerun()


def _render_setup_instructions() -> None:
    """Render the API credentials setup instructions"""
    with st.expander("ℹ️ How to get free API credentials (2 minutes)", expanded=False):
        st.markdown("""
        **Quick guide to get your free IGDB credentials:**

        1. **Visit** [Twitch Developer Console](https://dev.twitch.tv/console/apps)
        2. **Login** with Twitch (or create a free account)
        3. **Click** "Register Your Application"
        4. **Fill in:**
           - Name: `Game Folder Renamer`
           - OAuth Redirect: `http://localhost`
           - Category: `Application Integration`
        5. **Click** "Create" then "Manage"
        6. **Copy** your Client ID and Client Secret
        7. **Paste** them in the form below

        That's it! The credentials are free and work forever.
        """)


def _render_setup_form(saved_config: Dict[str, Any]) -> None:
    """Render the setup form for credentials and folder path

    Args:
        saved_config: Previously saved configuration
    """
    default_client_id = saved_config.get('client_id', '')
    default_client_secret = saved_config.get('client_secret', '')
    default_games_folder = saved_config.get('games_folder', os.path.expanduser('~'))

    with st.form("setup_form"):
        st.write("### 🔐 API Credentials")

        client_id = st.text_input(
            "Client ID",
            value=default_client_id,
            type="password",
            placeholder="Paste your Client ID here"
        )

        client_secret = st.text_input(
            "Client Secret",
            value=default_client_secret,
            type="password",
            placeholder="Paste your Client Secret here"
        )

        st.write("### 📁 Games Folder")

        games_folder = st.text_input(
            "Folder Path",
            value=default_games_folder,
            placeholder="e.g., /home/user/games or C:\\Games",
            help="The folder that contains all your game folders"
        )

        save_settings = st.checkbox(
            "Save these settings for next time",
            value=True,
            help="Settings will be saved to ~/.game_renamer_config.yaml"
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🔌 Connect to IGDB", use_container_width=True, type="primary")

    if submitted:
        _handle_form_submission(client_id, client_secret, games_folder, save_settings)


def _handle_form_submission(
    client_id: str,
    client_secret: str,
    games_folder: str,
    save_settings: bool
) -> None:
    """Handle the setup form submission

    Args:
        client_id: IGDB client ID
        client_secret: IGDB client secret
        games_folder: Path to games folder
        save_settings: Whether to save settings to config file
    """
    # Expand user path
    expanded_folder = os.path.expanduser(games_folder)

    # Validate inputs
    error = _validate_credentials(client_id, client_secret, expanded_folder)
    if error:
        st.error(f"❌ {error}")
        return

    try:
        with st.spinner("🔄 Authenticating with IGDB..."):
            # Use cached authentication
            igdb_client = get_authenticated_igdb_client(client_id, client_secret)

            # Store in session state
            st.session_state.igdb_client = igdb_client
            st.session_state.renamer = GameFolderRenamer(igdb_client, expanded_folder)
            st.session_state.client_id = client_id
            st.session_state.client_secret = client_secret

            # Save settings if requested
            if save_settings:
                config = {
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'games_folder': expanded_folder
                }
                if save_config(config):
                    st.success("✅ Settings saved successfully")

        st.success("✅ Connected successfully!")
        st.info("💡 Use the sidebar to navigate to 'Scan & Process' to start renaming your game folders.")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Authentication failed: {str(e)}")
        st.info("💡 Please check your credentials and try again. Make sure there are no extra spaces.")

        # Additional troubleshooting hints
        with st.expander("🔍 Troubleshooting tips"):
            st.markdown("""
            - Verify your Client ID and Client Secret are correct
            - Make sure you copied the entire credential without extra spaces
            - Check your internet connection
            - Try regenerating credentials in the Twitch Developer Console
            - Ensure the credentials are for the same application
            """)


def show() -> None:
    """Display the Setup/Configuration page"""
    st.title("🔑 Setup")
    st.markdown("Get started by connecting to IGDB and selecting your games folder")

    # Load saved configuration
    saved_config = load_config()

    # Check if already connected
    if st.session_state.get('igdb_client'):
        _render_disconnect_section()
    else:
        st.divider()
        _render_setup_instructions()
        st.divider()
        _render_setup_form(saved_config)
