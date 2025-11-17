import streamlit as st
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from game_renamer import IGDBClient
from platforms import PlatformManager

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


def _render_credentials_section(saved_config: Dict[str, Any]) -> None:
    """Render API credentials section"""
    st.write("### 🔐 API Credentials")

    with st.expander("ℹ️ How to get free API credentials", expanded=False):
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

    col1, col2 = st.columns(2)

    with col1:
        client_id = st.text_input(
            "Client ID",
            value=saved_config.get('client_id', ''),
            type="password",
            placeholder="Paste your Client ID here",
            key="input_client_id"
        )

    with col2:
        client_secret = st.text_input(
            "Client Secret",
            value=saved_config.get('client_secret', ''),
            type="password",
            placeholder="Paste your Client Secret here",
            key="input_client_secret"
        )

    # Test connection button
    if client_id and client_secret:
        if st.button("🔌 Test Connection"):
            try:
                with st.spinner("🔄 Authenticating with IGDB..."):
                    igdb_client = get_authenticated_igdb_client(client_id, client_secret)
                    st.session_state.igdb_client = igdb_client
                    st.session_state.client_id = client_id
                    st.session_state.client_secret = client_secret
                    st.session_state.igdb_connection_failed = False  # Clear failed flag

                    # Create platform manager
                    st.session_state.platform_manager = PlatformManager(client_id, igdb_client.access_token)

                with st.spinner("🎮 Loading platforms from IGDB..."):
                    # Pre-fetch platforms to cache them
                    platforms = st.session_state.platform_manager.fetch_all_platforms()
                    st.success(f"✅ Connected successfully! Loaded {len(platforms)} platforms")
                    st.rerun()
            except Exception as e:
                st.session_state.igdb_connection_failed = True  # Set failed flag
                st.error(f"❌ Authentication failed: {str(e)}")
    else:
        st.info("👆 Enter your credentials above and click 'Test Connection'")


def _render_folder_management() -> None:
    """Render the folder management section"""
    st.write("### 📁 Platform Folders")
    st.markdown("Configure which folders contain games for each platform")

    # Initialize folder_configs in session state if not exists
    if 'folder_configs' not in st.session_state:
        # Load from saved config
        saved_config = load_config()
        st.session_state.folder_configs = saved_config.get('folder_configs', [])

    # Get platform choices
    platform_manager = st.session_state.get('platform_manager')
    if not platform_manager:
        st.warning("⚠️ Please connect to IGDB first")
        return

    try:
        platforms = platform_manager.fetch_all_platforms()

        # Define popular platform IDs
        popular_platform_ids = [
            6,    # PC (Microsoft Windows)
            48,   # PlayStation 4
            49,   # Xbox One
            130,  # Nintendo Switch
            167,  # PlayStation 5
            169,  # Xbox Series X|S
            9,    # PlayStation 3
            12,   # Xbox 360
            41,   # Wii U
            5,    # Wii
            7,    # PlayStation
            8,    # PlayStation 2
        ]

        # Separate popular and other platforms
        popular_platforms = []
        other_platforms = []

        for p in platforms:
            display_name = platform_manager.get_platform_display_name(p)
            if p['id'] in popular_platform_ids:
                popular_platforms.append((p['id'], display_name))
            else:
                other_platforms.append((p['id'], display_name))

        # Sort popular platforms by the order in popular_platform_ids
        popular_platforms.sort(key=lambda x: popular_platform_ids.index(x[0]) if x[0] in popular_platform_ids else 999)

        # Sort other platforms alphabetically
        other_platforms.sort(key=lambda x: x[1])

        # Combine with separator
        platform_options = popular_platforms + [(-1, "────────────────────")] + other_platforms
        platform_lookup = {p['id']: platform_manager.get_platform_display_name(p) for p in platforms}
    except Exception as e:
        st.error(f"❌ Failed to load platforms: {str(e)}")
        return

    # Combined section for managing folders
    # Header row for labels
    col1, col2, col3 = st.columns([3, 5, 1])
    with col1:
        st.markdown("**Platform**")
    with col2:
        st.markdown("**Folder Path**")
    with col3:
        st.markdown("**Action**")

    # Use form to ensure consistent alignment
    with st.form("add_folder_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([3, 5, 1])

        with col1:
            # Platform dropdown
            platform_names = [name for _, name in platform_options]
            selected_platform_name = st.selectbox(
                "Platform",
                platform_names,
                key="new_platform_select_form",
                placeholder="Select Platform",
                label_visibility="collapsed"
            )

            # Get selected platform ID (skip separator)
            selected_platform_id = next((pid for pid, name in platform_options if name == selected_platform_name and pid != -1), None)

        with col2:
            # Folder path input
            new_folder = st.text_input(
                "Folder Path",
                placeholder="C:\\Games or /home/user/games",
                key="new_folder_input_form",
                label_visibility="collapsed"
            )

        with col3:
            submitted = st.form_submit_button("Add", use_container_width=True, type="primary")

    # Handle form submission outside the form
    if submitted:
        # Check if separator was selected
        if selected_platform_id is None or selected_platform_id == -1:
            st.error("❌ Please select a valid platform")
        elif new_folder:
            expanded_path = os.path.expanduser(new_folder)

            # Validate path
            if not os.path.exists(expanded_path):
                st.error(f"❌ Folder does not exist: {expanded_path}")
            elif not os.path.isdir(expanded_path):
                st.error(f"❌ Path is not a directory: {expanded_path}")
            elif not os.access(expanded_path, os.R_OK):
                st.error(f"❌ No read permission for folder: {expanded_path}")
            else:
                # Add to folder configs
                new_config = {
                    'platform_id': selected_platform_id,
                    'folder_path': expanded_path
                }

                # Check for duplicates
                if new_config not in st.session_state.folder_configs:
                    st.session_state.folder_configs.append(new_config)
                    st.success(f"✅ Added {platform_lookup[selected_platform_id]} folder")
                    st.rerun()
                else:
                    st.warning("⚠️ This folder is already configured")
        else:
            st.error("❌ Please enter a folder path")

    # Display existing folder configurations below the form
    if st.session_state.folder_configs:
        st.divider()
        st.write("**Configured Folders:**")

        for idx, config in enumerate(st.session_state.folder_configs):
            platform_id = config['platform_id']
            folder_path = config['folder_path']
            platform_name = platform_lookup.get(platform_id, f"Platform {platform_id}")

            col1, col2, col3 = st.columns([3, 5, 1])

            with col1:
                st.text(f"🎮 {platform_name}")

            with col2:
                st.text(f"📂 {folder_path}")

            with col3:
                if st.button("🗑️", key=f"delete_{idx}", help="Remove this folder"):
                    st.session_state.folder_configs.pop(idx)
                    st.rerun()


def _render_save_section() -> None:
    """Render the save configuration section"""
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
            # Prepare config to save
            config = {
                'client_id': st.session_state.get('client_id', ''),
                'client_secret': st.session_state.get('client_secret', ''),
                'folder_configs': st.session_state.get('folder_configs', [])
            }

            if save_config(config):
                st.success("✅ Configuration saved successfully!")
                st.info("💡 Go to **Scan & Process** to start renaming your games")
            else:
                st.error("❌ Failed to save configuration")


def show() -> None:
    """Display the Setup/Configuration page"""
    st.title("🔑 Setup")
    st.markdown("Configure your IGDB credentials and game folder locations")

    # Load saved configuration
    saved_config = load_config()

    # Auto-load credentials if available
    if saved_config.get('client_id') and saved_config.get('client_secret') and not st.session_state.get('igdb_client'):
        try:
            igdb_client = get_authenticated_igdb_client(saved_config['client_id'], saved_config['client_secret'])
            st.session_state.igdb_client = igdb_client
            st.session_state.client_id = saved_config['client_id']
            st.session_state.client_secret = saved_config['client_secret']
            st.session_state.platform_manager = PlatformManager(saved_config['client_id'], igdb_client.access_token)

            # Pre-fetch and cache platforms
            try:
                st.session_state.platform_manager.fetch_all_platforms()
            except:
                pass  # Silently continue if platform fetch fails during auto-load
        except:
            pass  # Silently continue - will reconnect when needed

    st.divider()

    # Render credentials section
    _render_credentials_section(saved_config)

    st.divider()

    # Render folder management (only if connected)
    if st.session_state.get('igdb_client'):
        _render_folder_management()
        _render_save_section()
    else:
        st.info("👆 Connect to IGDB first to configure your game folders")
