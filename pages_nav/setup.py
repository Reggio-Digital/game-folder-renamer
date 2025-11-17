import streamlit as st
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from game_renamer import IGDBClient
from platforms import PlatformManager

# Configuration file management
CONFIG_FILE = Path.home() / '.game_folder_renamer_config.yaml'


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


def get_template_for_platform(platform_id: int) -> str:
    """Get the rename template for a specific platform

    Args:
        platform_id: IGDB platform ID

    Returns:
        Template string for the platform, or default template if not configured
    """
    from game_renamer import DEFAULT_RENAME_TEMPLATE

    config = load_config()
    templates = config.get('rename_templates', {})

    # Check for platform-specific template
    platform_templates = templates.get('platforms', {})
    if platform_id in platform_templates:
        return platform_templates[platform_id]

    # Fall back to default template
    return templates.get('default', DEFAULT_RENAME_TEMPLATE)


def save_template_for_platform(platform_id: int, template: str) -> bool:
    """Save a rename template for a specific platform

    Args:
        platform_id: IGDB platform ID
        template: Template string

    Returns:
        True if successful, False otherwise
    """
    config = load_config()

    # Initialize templates structure if not exists
    if 'rename_templates' not in config:
        config['rename_templates'] = {'platforms': {}}
    if 'platforms' not in config['rename_templates']:
        config['rename_templates']['platforms'] = {}

    # Save template
    config['rename_templates']['platforms'][platform_id] = template

    return save_config(config)


def save_default_template(template: str) -> bool:
    """Save the default rename template

    Args:
        template: Template string

    Returns:
        True if successful, False otherwise
    """
    config = load_config()

    # Initialize templates structure if not exists
    if 'rename_templates' not in config:
        config['rename_templates'] = {}

    # Save default template
    config['rename_templates']['default'] = template

    return save_config(config)


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
        platform_data_lookup = {p['id']: p for p in platforms}  # Full platform data for logos
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

        # Create table header
        header_cols = st.columns([4, 6, 1])
        with header_cols[0]:
            st.markdown("**Platform**")
        with header_cols[1]:
            st.markdown("**Folder Path**")
        with header_cols[2]:
            st.markdown("")

        st.divider()

        for idx, config in enumerate(st.session_state.folder_configs):
            platform_id = config['platform_id']
            folder_path = config['folder_path']
            platform_name = platform_lookup.get(platform_id, f"Platform {platform_id}")

            col1, col2, col3 = st.columns([4, 6, 1])

            with col1:
                st.text(platform_name)

            with col2:
                st.text(folder_path)

            with col3:
                if st.button("🗑️", key=f"delete_{idx}", help="Remove this folder"):
                    st.session_state.folder_configs.pop(idx)
                    st.rerun()


def _render_template_builder() -> None:
    """Render the rename template builder section"""
    from game_renamer import TemplateFormatter, DEFAULT_RENAME_TEMPLATE

    st.write("### 🎨 Rename Templates")
    st.markdown("Customize how game folders are renamed for each platform")

    with st.expander("ℹ️ How templates work", expanded=False):
        st.markdown("""
        **Templates** let you customize how game folders are renamed using special tokens.

        **Available tokens:**
        """)
        for token, description in TemplateFormatter.AVAILABLE_TOKENS.items():
            st.markdown(f"- `{token}` - {description}")

        st.markdown("""
        **Examples:**
        - `{name} ({year})` → "The Witcher 3: Wild Hunt (2015)"
        - `{name} [{platform}] ({year})` → "Mario Kart 8 [Switch] (2014)"
        - `{name} ({year}) - {developer}` → "Cyberpunk 2077 (2020) - CD Projekt RED"
        - `{name} ({year}) [{genres}]` → "Elden Ring (2022) [Role-playing, Adventure]"
        """)

    # Get current config
    config = load_config()
    templates = config.get('rename_templates', {})
    default_template = templates.get('default', DEFAULT_RENAME_TEMPLATE)

    # Default template section
    st.write("#### Default Template")
    st.markdown("This template is used when no platform-specific template is set")

    col1, col2 = st.columns([3, 1])

    with col1:
        new_default = st.text_input(
            "Default template",
            value=default_template,
            key="default_template_input",
            label_visibility="collapsed",
            placeholder="{name} ({year})"
        )

    with col2:
        if st.button("💾 Save Default", key="save_default_template", use_container_width=True):
            is_valid, error_msg = TemplateFormatter.validate_template(new_default)
            if is_valid:
                if save_default_template(new_default):
                    st.success("✅ Default template saved!")
                    st.rerun()
            else:
                st.error(f"❌ {error_msg}")

    # Preview default template
    if new_default:
        preview = TemplateFormatter.get_preview(new_default)
        st.markdown(f"**Preview:** `{preview}`")

    # Token chips for easy insertion
    st.write("**Click to add tokens:**")
    token_cols = st.columns(5)
    tokens = list(TemplateFormatter.AVAILABLE_TOKENS.keys())
    for i, token in enumerate(tokens):
        with token_cols[i % 5]:
            if st.button(token, key=f"default_token_{i}", use_container_width=True):
                # This would ideally insert at cursor, but Streamlit doesn't support that
                # So we'll just show the token
                st.info(f"Copy and paste: `{token}`")

    st.divider()

    # Platform-specific templates
    st.write("#### Platform-Specific Templates")
    st.markdown("Override the default template for specific platforms")

    # Get configured folders to show platform-specific templates
    folder_configs = st.session_state.get('folder_configs', [])

    if not folder_configs:
        st.info("👆 Configure platform folders above to set platform-specific templates")
        return

    # Get platform manager
    platform_manager = st.session_state.get('platform_manager')
    if not platform_manager:
        return

    try:
        platforms = platform_manager.fetch_all_platforms()
        platform_lookup = {p['id']: platform_manager.get_platform_display_name(p) for p in platforms}
    except Exception as e:
        st.error(f"❌ Failed to load platforms: {str(e)}")
        return

    # Get unique platform IDs from configured folders
    configured_platform_ids = list(set(fc['platform_id'] for fc in folder_configs))
    configured_platform_ids.sort(key=lambda pid: platform_lookup.get(pid, ""))

    platform_templates = templates.get('platforms', {})

    for platform_id in configured_platform_ids:
        platform_name = platform_lookup.get(platform_id, f"Platform {platform_id}")
        current_template = platform_templates.get(platform_id, default_template)

        with st.container():
            st.write(f"**{platform_name}**")

            col1, col2 = st.columns([3, 1])

            with col1:
                new_template = st.text_input(
                    f"Template for {platform_name}",
                    value=current_template,
                    key=f"template_{platform_id}",
                    label_visibility="collapsed",
                    placeholder=default_template
                )

            with col2:
                if st.button("💾 Save", key=f"save_template_{platform_id}", use_container_width=True):
                    is_valid, error_msg = TemplateFormatter.validate_template(new_template)
                    if is_valid:
                        if save_template_for_platform(platform_id, new_template):
                            st.success(f"✅ Template saved for {platform_name}!")
                            st.rerun()
                    else:
                        st.error(f"❌ {error_msg}")

            # Preview
            if new_template:
                # Get platform abbreviation for preview
                platform_data = next((p for p in platforms if p['id'] == platform_id), None)
                platform_abbr = platform_data.get('abbreviation', '') if platform_data else ''

                sample_data = {
                    "name": "The Witcher 3: Wild Hunt",
                    "year": "2015",
                    "developers": ["CD Projekt RED"],
                    "publishers": ["CD Projekt"],
                    "genres": ["Role-playing", "Adventure"],
                    "platforms": [platform_abbr] if platform_abbr else [],
                    "rating": 9.2,
                    "aggregated_rating": 9.3,
                    "version_title": "Complete Edition"
                }

                preview = TemplateFormatter.format(new_template, sample_data, platform_abbr)
                st.markdown(f"**Preview:** `{preview}`")

            st.divider()


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

        st.divider()

        # Render template builder
        _render_template_builder()

        _render_save_section()
    else:
        st.info("👆 Connect to IGDB first to configure your game folders")
