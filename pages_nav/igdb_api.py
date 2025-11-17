import streamlit as st
from pages_nav.setup import load_config, save_config, get_authenticated_igdb_client
from platforms import PlatformManager


def show():
    """Display the IGDB API Configuration page"""
    st.title("🔐 IGDB API Configuration")
    st.markdown("Configure your IGDB API credentials to access the game database")

    # Load saved configuration
    saved_config = load_config()

    # Auto-load credentials if available and not already loaded
    if saved_config.get('client_id') and saved_config.get('client_secret'):
        if not st.session_state.get('igdb_client'):
            try:
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
                # Failed to auto-load, user will need to test connection
                st.session_state.igdb_connection_failed = True

    st.divider()

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

    st.divider()

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

    st.divider()

    # Test connection button
    if client_id and client_secret:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔌 Test Connection", use_container_width=True, type="primary"):
                try:
                    with st.spinner("🔄 Authenticating with IGDB..."):
                        igdb_client = get_authenticated_igdb_client(client_id, client_secret)
                        st.session_state.igdb_client = igdb_client
                        st.session_state.client_id = client_id
                        st.session_state.client_secret = client_secret
                        st.session_state.igdb_connection_failed = False

                        # Create platform manager
                        st.session_state.platform_manager = PlatformManager(client_id, igdb_client.access_token)

                    with st.spinner("🎮 Loading platforms from IGDB..."):
                        # Pre-fetch platforms to cache them
                        platforms = st.session_state.platform_manager.fetch_all_platforms()

                        # Save credentials
                        config = load_config()
                        config['client_id'] = client_id
                        config['client_secret'] = client_secret
                        save_config(config)

                        st.success(f"✅ Connected successfully! Loaded {len(platforms)} platforms")
                        st.info("👉 Now go to **Platform Folders** to configure your game directories")
                except Exception as e:
                    st.session_state.igdb_connection_failed = True
                    st.error(f"❌ Authentication failed: {str(e)}")
    else:
        st.info("👆 Enter your credentials above and click 'Test Connection'")

    # Show current status
    st.divider()
    if st.session_state.get('igdb_client'):
        st.success("✅ Currently connected to IGDB")
        if st.session_state.get('platform_manager'):
            try:
                platforms = st.session_state.platform_manager.fetch_all_platforms()
                st.caption(f"📊 {len(platforms)} platforms available")
            except:
                pass
    else:
        st.warning("❌ Not connected - please enter credentials and test connection")
