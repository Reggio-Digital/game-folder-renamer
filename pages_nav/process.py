import streamlit as st

# Cached function for game searches
@st.cache_data(ttl=None)  # ttl=None means cache forever
def search_game_cached(client_id: str, client_secret: str, game_name: str):
    """Search for a game with forever caching"""
    from pages_nav.setup import get_authenticated_igdb_client
    client = get_authenticated_igdb_client(client_id, client_secret)
    return client.search_game(game_name)

def show():
    """Display the Scan & Process page"""
    st.title("🎮 Scan & Process Game Folders")
    st.markdown("Scan your games folder and rename folders using IGDB data")

    # Check if connected
    if not st.session_state.get('igdb_client'):
        st.warning("⚠️ Not connected to IGDB")
        st.info("Please configure your API credentials in the Setup page first.")
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
        if st.button("🔄 Process All Folders", use_container_width=True, disabled=len(st.session_state.get('folders', [])) == 0):
            st.session_state.processing_mode = True

    with col3:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.processing_results = {}
            st.session_state.pending_selections = {}
            st.rerun()

    # Show statistics
    if st.session_state.get('folders'):
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
            processed = len(st.session_state.get('processing_results', {}))
            st.metric("Processed", processed)

        st.divider()

    # Process folders if in processing mode
    if st.session_state.get('folders') and st.session_state.get('processing_mode'):
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

            # Search for game using cached function
            result = search_game_cached(
                st.session_state.client_id,
                st.session_state.client_secret,
                folder_name
            )
            if 'processing_results' not in st.session_state:
                st.session_state.processing_results = {}
            st.session_state.processing_results[folder_name] = result

        status_text.text("Processing complete!")
        st.rerun()

    # Display results
    if st.session_state.get('processing_results'):
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
    elif st.session_state.get('folders'):
        st.subheader("📁 Scanned Folders")

        for folder in st.session_state.folders:
            if folder['already_named']:
                st.success(f"✅ {folder['name']} (already properly named)")
            else:
                st.info(f"📁 {folder['name']}")
