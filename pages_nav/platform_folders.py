import streamlit as st
import os
from pages_nav.setup import load_config, save_config


def show():
    """Display the Platform Folders Configuration page"""
    st.title("📁 Platform Folders")
    st.markdown("Configure which folders contain games for each platform")

    # Auto-load credentials if available and not already loaded
    saved_config = load_config()
    if saved_config.get('client_id') and saved_config.get('client_secret'):
        if not st.session_state.get('igdb_client'):
            try:
                from pages_nav.setup import get_authenticated_igdb_client
                from platforms import PlatformManager

                with st.spinner("Loading saved credentials..."):
                    igdb_client = get_authenticated_igdb_client(
                        saved_config['client_id'],
                        saved_config['client_secret']
                    )
                    st.session_state.igdb_client = igdb_client
                    st.session_state.client_id = saved_config['client_id']
                    st.session_state.client_secret = saved_config['client_secret']
                    st.session_state.igdb_connection_failed = False
                    st.session_state.platform_manager = PlatformManager(
                        saved_config['client_id'],
                        igdb_client.access_token
                    )
                    # Pre-fetch platforms
                    st.session_state.platform_manager.fetch_all_platforms()
            except:
                st.session_state.igdb_connection_failed = True

    # Check if connected
    if not st.session_state.get('igdb_client'):
        st.warning("⚠️ You need to connect to IGDB first")
        st.info("👉 Go to the **IGDB API** page to configure your credentials")
        st.stop()

    st.divider()

    # Initialize folder_configs in session state if not exists
    if 'folder_configs' not in st.session_state:
        # Load from saved config
        saved_config = load_config()
        st.session_state.folder_configs = saved_config.get('folder_configs', [])

    # Get platform manager
    platform_manager = st.session_state.get('platform_manager')
    if not platform_manager:
        st.error("⚠️ Platform manager not initialized. Please reconnect on the IGDB API page.")
        st.stop()

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
        st.stop()

    # Add folder section
    st.write("### ➕ Add New Folder")

    # Header row for labels
    col1, col2, col3 = st.columns([3, 5, 1])
    with col1:
        st.markdown("**Platform**")
    with col2:
        st.markdown("**Folder Path**")
    with col3:
        st.markdown("**Action**")

    # Use form for adding folders
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

    # Handle form submission
    if submitted:
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

                    # Save immediately
                    config = load_config()
                    config['folder_configs'] = st.session_state.folder_configs
                    save_config(config)

                    st.success(f"✅ Added {platform_lookup[selected_platform_id]} folder")
                    st.rerun()
                else:
                    st.warning("⚠️ This folder is already configured")
        else:
            st.error("❌ Please enter a folder path")

    # Display existing folder configurations
    if st.session_state.folder_configs:
        st.divider()
        st.write("### 📂 Configured Folders")

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

                    # Save immediately
                    config = load_config()
                    config['folder_configs'] = st.session_state.folder_configs
                    save_config(config)

                    st.rerun()
    else:
        st.info("👆 No folders configured yet. Add your first folder above!")
        st.markdown("""
        **Tip:** Your game folders should contain subfolders for individual games.
        For example:
        - `C:\\Games\\PC\\` might contain `The Witcher 3`, `Cyberpunk 2077`, etc.
        - `/home/user/games/switch/` might contain `Mario Kart 8`, `Zelda BOTW`, etc.
        """)
