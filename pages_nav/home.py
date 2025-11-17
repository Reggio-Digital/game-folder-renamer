import streamlit as st

def show():
    """Display the Home/Dashboard page with getting started guide"""
    st.title("🎮 Game Folder Renamer")
    st.markdown("Automatically rename your game folders with IGDB data")

    st.divider()

    # Check connection status and show appropriate guidance
    is_connected = st.session_state.get('igdb_client') is not None
    has_folders = len(st.session_state.get('folders', [])) > 0
    has_results = len(st.session_state.get('processing_results', {})) > 0

    if not is_connected:
        # Step 1: Not connected - guide to setup
        st.markdown("### 🚀 Let's Get Started!")
        st.info("**Step 1:** Configure your IGDB API credentials to begin")

        st.markdown("""
        #### What you'll need:
        - Free IGDB API credentials from Twitch Developer Console
        - Path to your games folder

        #### Quick setup (takes ~2 minutes):
        1. Visit [Twitch Developer Console](https://dev.twitch.tv/console/apps)
        2. Create a free account if needed
        3. Register a new application
        4. Copy your Client ID and Client Secret
        5. Click the **Setup** page in the sidebar to configure
        """)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("👈 **Click 'Setup' in the sidebar to begin**")

    elif not has_folders:
        # Step 2: Connected but no folders scanned
        st.success("✅ You're connected to IGDB!")
        st.markdown("### 📁 Next Step: Scan Your Game Folders")

        st.info("**Step 2:** Scan your games folder to see what needs renaming")

        if st.session_state.get('renamer'):
            st.markdown(f"**Your games folder:** `{st.session_state.renamer.base_path}`")

        st.markdown("""
        #### What happens when you scan:
        - The app will list all folders in your games directory
        - It will identify which folders are already properly named
        - You'll see how many folders need renaming
        """)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("👈 **Click 'Scan & Process' in the sidebar**")

    elif not has_results:
        # Step 3: Folders scanned but not processed
        st.success("✅ You're connected and folders are scanned!")
        st.markdown("### 🔄 Next Step: Process Folders")

        total_folders = len(st.session_state.folders)
        already_named = sum(1 for f in st.session_state.folders if f['already_named'])
        to_process = total_folders - already_named

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Folders", total_folders)
        with col2:
            st.metric("Already Named", already_named)
        with col3:
            st.metric("To Process", to_process)

        st.info("**Step 3:** Process folders to get rename suggestions from IGDB")

        st.markdown("""
        #### What processing does:
        - Searches IGDB for each game folder
        - Finds the correct game name and release year
        - Suggests the proper folder name format
        - Lets you review before renaming
        """)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("👈 **Go to 'Scan & Process' to continue**")

    else:
        # Step 4: All done - show results
        st.success("✅ You're all set and processing is complete!")
        st.markdown("### 📊 Your Results")

        # Show results summary
        single_matches = sum(1 for r in st.session_state.processing_results.values()
                           if isinstance(r, dict) and r.get('status') == 'single_match')
        multiple_matches = sum(1 for r in st.session_state.processing_results.values()
                             if isinstance(r, dict) and r.get('status') == 'multiple_matches')
        not_found = sum(1 for r in st.session_state.processing_results.values()
                       if isinstance(r, dict) and r.get('status') == 'not_found')
        renamed = sum(1 for r in st.session_state.processing_results.values()
                     if isinstance(r, dict) and r.get('status') == 'renamed')

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Auto-Matched", single_matches, help="Ready to rename with one click")
        with col2:
            st.metric("Need Selection", multiple_matches, help="Multiple games found - you choose")
        with col3:
            st.metric("Already Renamed", renamed, help="Successfully renamed folders")
        with col4:
            st.metric("Not Found", not_found, help="No match in IGDB database")

        st.divider()

        if single_matches > 0 or multiple_matches > 0:
            st.info("**Next:** Go to 'Scan & Process' to review and rename your folders")
        else:
            st.success("🎉 All folders have been processed!")

        st.markdown("""
        #### What you can do now:
        - Review and rename matched folders in **Scan & Process**
        - Scan again to pick up any new folders
        - Reconfigure settings in **Setup** if needed
        """)

    st.divider()

    # Quick tips section
    with st.expander("💡 Tips for Best Results"):
        st.markdown("""
        - **Folder names**: The app handles various formats (dots, underscores, version numbers)
        - **Already named**: Folders matching `Game Name (Year)` format are automatically skipped
        - **Multiple matches**: When multiple games are found, you can choose the correct one
        - **Not found**: Some indie or very new games might not be in IGDB yet
        - **Cached results**: Search results are cached for faster repeated operations
        """)

    # Show example transformations
    with st.expander("📝 Example Transformations"):
        st.markdown("""
        Here's how the app renames folders:

        | Original Folder Name | Renamed To |
        |---------------------|------------|
        | `The.Witcher.3-CODEX` | `The Witcher 3: Wild Hunt (2015)` |
        | `Cyberpunk.2077.v1.5` | `Cyberpunk 2077 (2020)` |
        | `HalfLife2` | `Half-Life 2 (2004)` |
        | `Portal.2.Enhanced.Edition` | `Portal 2 (2011)` |
        | `GTA.V-RELOADED` | `Grand Theft Auto V (2015)` |
        """)
