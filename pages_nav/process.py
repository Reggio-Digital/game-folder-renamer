import streamlit as st
import os
from typing import Dict, List, Tuple, Any, Optional
from utils import format_game_name, format_game_option, get_remake_badge
from game_renamer import GameFolderRenamer


# Cached function for game searches
@st.cache_data(ttl=None)  # ttl=None means cache forever
def search_game_cached(client_id: str, client_secret: str, game_name: str, platform_id: int) -> Dict[str, Any]:
    """Search for a game with forever caching

    Args:
        client_id: IGDB client ID
        client_secret: IGDB client secret
        game_name: Name of the game to search for
        platform_id: Platform ID to filter by

    Returns:
        Search result dictionary from IGDB
    """
    from pages_nav.setup import get_authenticated_igdb_client
    client = get_authenticated_igdb_client(client_id, client_secret)
    return client.search_game(game_name, platform_id)


def _check_connection() -> bool:
    """Check if user is connected to IGDB and show warning if not

    Returns:
        True if connected, False otherwise
    """
    if not st.session_state.get('igdb_client'):
        st.warning("⚠️ You need to connect to IGDB first")
        st.info("👉 Go to the **Setup** page to configure your credentials")
        return False
    return True


def _render_folder_selector() -> Optional[Tuple[int, str, str]]:
    """Render folder selector from configured folders

    Returns:
        Tuple of (platform_id, folder_path, display_name) or None
    """
    folder_configs = st.session_state.get('folder_configs', [])

    if not folder_configs:
        st.warning("⚠️ No game folders configured")
        st.info("👉 Go to the **Setup** page to add your game folders")
        return None

    # Get platform manager for display names
    platform_manager = st.session_state.get('platform_manager')
    if not platform_manager:
        st.error("⚠️ Platform manager not initialized")
        return None

    # Build display options
    display_options = []
    for config in folder_configs:
        platform_id = config['platform_id']
        folder_path = config['folder_path']

        # Get platform info
        try:
            platforms = platform_manager.fetch_all_platforms()
            platform = next((p for p in platforms if p['id'] == platform_id), None)
            if platform:
                platform_name = platform_manager.get_platform_display_name(platform)
            else:
                platform_name = f"Platform {platform_id}"
        except:
            platform_name = f"Platform {platform_id}"

        folder_name = os.path.basename(folder_path)
        display = f"{platform_name} - {folder_name}"
        display_options.append((platform_id, folder_path, display, platform_name))

    # Current selection
    current_idx = 0
    if 'current_folder_config_idx' in st.session_state:
        current_idx = st.session_state.current_folder_config_idx
        if current_idx >= len(display_options):
            current_idx = 0

    # Render selector
    st.write("### 🎮 Select Folder to Process")

    selected_display = st.selectbox(
        "Folder",
        [opt[2] for opt in display_options],
        index=current_idx,
        help="Select which folder's games to process"
    )

    # Get selected config
    selected_idx = [opt[2] for opt in display_options].index(selected_display)
    platform_id, folder_path, display, platform_name = display_options[selected_idx]

    # Update renamer if folder changed
    if st.session_state.get('current_folder_config_idx') != selected_idx:
        st.session_state.renamer = GameFolderRenamer(
            st.session_state.igdb_client,
            folder_path,
            platform_id
        )
        st.session_state.current_folder_config_idx = selected_idx
        st.session_state.current_platform_id = platform_id
        st.session_state.current_platform_name = platform_name
        st.session_state.current_folder_path = folder_path

        # Clear previous results when switching folders
        st.session_state.folders = []
        st.session_state.processing_results = {}

    st.info(f"📁 Processing: **{platform_name}** from `{folder_path}`")
    st.divider()

    return (platform_id, folder_path, platform_name)


def _render_action_buttons() -> None:
    """Render the main action buttons (Scan, Process, Clear)"""
    # Dry-run toggle
    st.session_state.dry_run = st.checkbox(
        "🔍 Dry Run Mode (Preview changes without actually renaming)",
        value=st.session_state.get('dry_run', False),
        help="When enabled, rename operations will only show what would happen without actually renaming folders"
    )

    if st.session_state.dry_run:
        st.info("ℹ️ Dry Run Mode is enabled - no folders will be renamed")

    st.divider()

    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        if st.button("🔍 Scan Folders", use_container_width=True):
            _handle_scan_folders()

    with col2:
        folders_exist = len(st.session_state.get('folders', [])) > 0
        if st.button("🔄 Process All Folders", use_container_width=True, disabled=not folders_exist):
            st.session_state.processing_mode = True

    with col3:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.processing_results = {}
            st.session_state.pending_selections = {}
            st.rerun()


def _handle_scan_folders() -> None:
    """Handle the scan folders button action"""
    with st.spinner("Scanning folders..."):
        try:
            folders = st.session_state.renamer.get_folders()
            st.session_state.folders = folders
            st.session_state.processing_results = {}
            st.session_state.pending_selections = {}
            st.rerun()
        except OSError as e:
            st.error(f"Error scanning folders: {str(e)}")


def _render_statistics() -> None:
    """Render the statistics section showing folder counts"""
    if not st.session_state.get('folders'):
        return

    st.divider()

    total_folders = len(st.session_state.folders)
    already_named = sum(1 for f in st.session_state.folders if f['already_named'])
    to_process = total_folders - already_named
    processed = len(st.session_state.get('processing_results', {}))

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric("Total Folders", total_folders)
    with stat_col2:
        st.metric("Already Named", already_named)
    with stat_col3:
        st.metric("To Process", to_process)
    with stat_col4:
        st.metric("Processed", processed)

    st.divider()


def _process_folders() -> None:
    """Process all folders that need renaming"""
    if not (st.session_state.get('folders') and st.session_state.get('processing_mode')):
        return

    st.session_state.processing_mode = False

    progress_bar = st.progress(0)
    status_text = st.empty()

    folders_to_process = [f for f in st.session_state.folders if not f['already_named']]
    total = len(folders_to_process)

    for idx, folder in enumerate(folders_to_process):
        folder_name = folder['name']

        # Skip if already processed
        if folder_name in st.session_state.get('processing_results', {}):
            continue

        status_text.text(f"Processing {idx + 1}/{total}: {folder_name}")
        progress_bar.progress((idx + 1) / total)

        # Get current platform ID
        platform_id = st.session_state.get('current_platform_id', 6)

        # Search for game using cached function
        try:
            result = search_game_cached(
                st.session_state.client_id,
                st.session_state.client_secret,
                folder_name,
                platform_id
            )
        except Exception as e:
            # Mark connection as failed if API call fails
            st.session_state.igdb_connection_failed = True
            st.error(f"❌ IGDB connection failed: {str(e)}")
            st.info("👉 Go to **Setup** page and click 'Test Connection' to reconnect")
            return

        if 'processing_results' not in st.session_state:
            st.session_state.processing_results = {}

        st.session_state.processing_results[folder_name] = result

    status_text.text("Processing complete!")
    st.rerun()


def _categorize_results() -> Tuple[List, List, List, List, List]:
    """Categorize processing results by status

    Returns:
        Tuple of (single_matches, multiple_matches, not_found, errors, renamed)
    """
    single_matches = []
    multiple_matches = []
    not_found = []
    errors = []
    renamed = []

    for folder_name, result in st.session_state.processing_results.items():
        if not isinstance(result, dict):
            continue

        status = result.get('status')
        if status == 'single_match':
            single_matches.append((folder_name, result))
        elif status == 'multiple_matches':
            multiple_matches.append((folder_name, result))
        elif status == 'not_found':
            not_found.append(folder_name)
        elif status == 'error':
            errors.append((folder_name, result.get('message', 'Unknown error')))
        elif status == 'renamed':
            renamed.append((folder_name, result))

    return single_matches, multiple_matches, not_found, errors, renamed


def _render_single_match_item(folder_name: str, result: Dict[str, Any]) -> None:
    """Render a single match item in the auto-renamed tab

    Args:
        folder_name: Original folder name
        result: Result dictionary containing game data
    """
    game = result['game']
    new_name = format_game_name(game)
    remake_badge = get_remake_badge(game)

    with st.expander(f"📁 {folder_name} → {new_name}{remake_badge}"):
        st.write(f"**Original:** {folder_name}")
        st.write(f"**New Name:** {new_name}")
        st.write(f"**Year:** {game['year']}")

        if game['is_remake']:
            st.info("This is a remake or remaster")

        if st.button("✅ Rename", key=f"rename_{folder_name}"):
            _handle_rename_folder(folder_name, new_name, result)


def _handle_rename_folder(folder_name: str, new_name: str, result: Dict[str, Any]) -> None:
    """Handle renaming a folder

    Args:
        folder_name: Original folder name
        new_name: New folder name
        result: Result dictionary to update
    """
    dry_run = st.session_state.get('dry_run', False)
    action = "Simulating rename" if dry_run else "Renaming"

    with st.spinner(f"{action} {folder_name}..."):
        rename_result = st.session_state.renamer.rename_folder(folder_name, new_name, dry_run=dry_run)

        if rename_result['success']:
            if rename_result.get('dry_run'):
                st.success(f"✅ DRY RUN: Would rename to: {new_name}")
                st.info("ℹ️ No actual changes were made. Disable dry-run mode to perform the rename.")
            else:
                st.success(f"Renamed to: {new_name}")
                result['status'] = 'renamed'
                st.rerun()
        else:
            st.error(f"Error: {rename_result['error']}")


def _render_single_matches_tab(single_matches: List[Tuple[str, Dict]]) -> None:
    """Render the auto-renamed tab with single match items

    Args:
        single_matches: List of (folder_name, result) tuples
    """
    if single_matches:
        for folder_name, result in single_matches:
            _render_single_match_item(folder_name, result)
    else:
        st.info("No single matches found")


def _render_multiple_match_item(folder_name: str, result: Dict[str, Any]) -> None:
    """Render a multiple match item with selection dropdown

    Args:
        folder_name: Original folder name
        result: Result dictionary containing multiple games
    """
    with st.expander(f"📁 {folder_name}"):
        st.write(f"**Original Folder:** {folder_name}")
        st.write(f"**Search Query:** {result['query']}")
        st.write("**Select the correct game:**")

        games = result['games']
        options = [format_game_option(game) for game in games]
        options.append("❌ Skip this folder")

        selected = st.selectbox(
            "Choose a game:",
            options,
            key=f"select_{folder_name}"
        )

        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            if st.button("✅ Apply", key=f"apply_{folder_name}"):
                _handle_apply_selection(folder_name, selected, options, games, result)


def _handle_apply_selection(
    folder_name: str,
    selected: str,
    options: List[str],
    games: List[Dict[str, Any]],
    result: Dict[str, Any]
) -> None:
    """Handle applying a user's game selection

    Args:
        folder_name: Original folder name
        selected: Selected option string
        options: List of all option strings
        games: List of game dictionaries
        result: Result dictionary to update
    """
    if selected == "❌ Skip this folder":
        st.info("Skipped")
    else:
        selected_idx = options.index(selected)
        if selected_idx < len(games):
            selected_game = games[selected_idx]
            new_name = format_game_name(selected_game)
            dry_run = st.session_state.get('dry_run', False)
            action = "Simulating rename" if dry_run else "Renaming"

            with st.spinner(f"{action} {folder_name}..."):
                rename_result = st.session_state.renamer.rename_folder(folder_name, new_name, dry_run=dry_run)

                if rename_result['success']:
                    if rename_result.get('dry_run'):
                        st.success(f"✅ DRY RUN: Would rename to: {new_name}")
                        st.info("ℹ️ No actual changes were made. Disable dry-run mode to perform the rename.")
                    else:
                        st.success(f"Renamed to: {new_name}")
                        result['status'] = 'renamed'
                        st.rerun()
                else:
                    st.error(f"Error: {rename_result['error']}")


def _render_multiple_matches_tab(multiple_matches: List[Tuple[str, Dict]]) -> None:
    """Render the needs selection tab with multiple match items

    Args:
        multiple_matches: List of (folder_name, result) tuples
    """
    if multiple_matches:
        for folder_name, result in multiple_matches:
            _render_multiple_match_item(folder_name, result)
    else:
        st.info("No folders with multiple matches")


def _render_not_found_tab(not_found: List[str]) -> None:
    """Render the not found tab

    Args:
        not_found: List of folder names not found in IGDB
    """
    if not_found:
        st.warning("The following folders could not be found in IGDB:")
        for folder_name in not_found:
            st.text(f"• {folder_name}")
    else:
        st.info("All folders were found in IGDB")


def _render_errors_tab(errors: List[Tuple[str, str]]) -> None:
    """Render the errors tab

    Args:
        errors: List of (folder_name, error_message) tuples
    """
    if errors:
        st.error("The following folders had errors:")
        for folder_name, error_msg in errors:
            st.text(f"• {folder_name}")
            if error_msg:
                st.caption(f"  Error: {error_msg}")
    else:
        st.info("No errors occurred")


def _render_results() -> None:
    """Render the processing results in tabs"""
    if not st.session_state.get('processing_results'):
        return

    st.subheader("📊 Processing Results")

    # Categorize results
    single_matches, multiple_matches, not_found, errors, renamed = _categorize_results()

    # Create tabs for different result types
    tab1, tab2, tab3, tab4 = st.tabs([
        f"✅ Auto-Matched ({len(single_matches)})",
        f"🤔 Needs Selection ({len(multiple_matches)})",
        f"❌ Not Found ({len(not_found)})",
        f"⚠️ Errors ({len(errors)})"
    ])

    with tab1:
        _render_single_matches_tab(single_matches)

    with tab2:
        _render_multiple_matches_tab(multiple_matches)

    with tab3:
        _render_not_found_tab(not_found)

    with tab4:
        _render_errors_tab(errors)


def _render_scanned_folders() -> None:
    """Render the list of scanned folders if no results yet"""
    if st.session_state.get('processing_results') or not st.session_state.get('folders'):
        return

    st.subheader("📁 Scanned Folders")

    for folder in st.session_state.folders:
        if folder['already_named']:
            st.success(f"✅ {folder['name']} (already properly named)")
        else:
            st.info(f"📁 {folder['name']}")


def show() -> None:
    """Display the Scan & Process page"""
    st.title("🎮 Scan & Process")
    st.markdown("Scan your games folder and rename folders with accurate game data")

    # Check if connected
    if not _check_connection():
        st.stop()

    # Render folder selector
    folder_info = _render_folder_selector()

    # Check if we have a valid folder selected
    if not folder_info:
        st.stop()

    # Check if we have a renamer instance
    if not st.session_state.get('renamer'):
        st.error("⚠️ Renamer not initialized. Please select a folder.")
        st.stop()

    # Render main UI components
    _render_action_buttons()
    _render_statistics()

    # Process folders if in processing mode
    _process_folders()

    # Display results or scanned folders
    _render_results()
    _render_scanned_folders()
