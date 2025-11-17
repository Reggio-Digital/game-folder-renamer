import streamlit as st
from pages_nav.setup import load_config, get_template_for_platform, save_template_for_platform, save_default_template
from game_renamer import TemplateFormatter, DEFAULT_RENAME_TEMPLATE


def show():
    """Display the Rename Templates Configuration page"""
    st.title("🎨 Rename Templates")
    st.markdown("Customize how game folders are renamed for each platform")

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

    # Info about templates
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

        **Note:** Empty fields are automatically removed. For example, if a game has no developer,
        `{name} ({year}) - {developer}` becomes just `{name} ({year})`.
        """)

    # Get current config
    config = load_config()
    templates = config.get('rename_templates', {})
    default_template = templates.get('default', DEFAULT_RENAME_TEMPLATE)

    # Default template section
    st.write("### 🌐 Default Template")
    st.markdown("This template is used for all platforms unless overridden below")

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

    # Token chips for easy reference
    st.write("**Available tokens (copy to use):**")
    token_cols = st.columns(5)
    tokens = list(TemplateFormatter.AVAILABLE_TOKENS.keys())
    for i, token in enumerate(tokens):
        with token_cols[i % 5]:
            st.code(token, language=None)

    st.divider()

    # Platform-specific templates
    st.write("### 🎮 Platform-Specific Templates")
    st.markdown("Override the default template for specific platforms")

    # Get configured folders to show platform-specific templates
    folder_configs = st.session_state.get('folder_configs', [])

    if not folder_configs:
        st.info("👆 No platform folders configured yet")
        st.markdown("Go to **Platform Folders** to add folders, then return here to customize templates per platform.")
        st.stop()

    # Get platform manager
    platform_manager = st.session_state.get('platform_manager')
    if not platform_manager:
        st.error("⚠️ Platform manager not initialized")
        st.stop()

    try:
        platforms = platform_manager.fetch_all_platforms()
        platform_lookup = {p['id']: platform_manager.get_platform_display_name(p) for p in platforms}
    except Exception as e:
        st.error(f"❌ Failed to load platforms: {str(e)}")
        st.stop()

    # Get unique platform IDs from configured folders
    configured_platform_ids = list(set(fc['platform_id'] for fc in folder_configs))
    configured_platform_ids.sort(key=lambda pid: platform_lookup.get(pid, ""))

    platform_templates = templates.get('platforms', {})

    for platform_id in configured_platform_ids:
        platform_name = platform_lookup.get(platform_id, f"Platform {platform_id}")
        current_template = platform_templates.get(platform_id, default_template)

        with st.container():
            st.write(f"#### {platform_name}")

            col1, col2 = st.columns([3, 1])

            with col1:
                new_template = st.text_input(
                    f"Template for {platform_name}",
                    value=current_template,
                    key=f"template_{platform_id}",
                    label_visibility="collapsed",
                    placeholder=default_template,
                    help=f"Leave as default or customize for {platform_name}"
                )

            with col2:
                if st.button("💾 Save", key=f"save_template_{platform_id}", use_container_width=True):
                    is_valid, error_msg = TemplateFormatter.validate_template(new_template)
                    if is_valid:
                        if save_template_for_platform(platform_id, new_template):
                            st.success(f"✅ Saved for {platform_name}!")
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
                    "version_title": "Complete Edition",
                    "game_modes": ["Single player"],
                    "themes": ["Fantasy", "Open world"],
                    "player_perspectives": ["Third person"],
                    "franchise": "The Witcher",
                    "region": "WW",
                    "slug": "the-witcher-3-wild-hunt",
                    "age_rating": "M"
                }

                preview = TemplateFormatter.format(new_template, sample_data, platform_abbr)
                st.markdown(f"**Preview:** `{preview}`")

            st.divider()
