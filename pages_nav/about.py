import streamlit as st

def show():
    """Display the About/Help page"""
    st.title("ℹ️ About Game Folder Renamer")

    st.markdown("""
    ## What is this app?

    **Game Folder Renamer** automatically renames your game folders using data from the IGDB
    (Internet Game Database). It helps you organize your game collection with consistent,
    properly formatted folder names.

    ### Features

    - 🔍 **Automatic Game Detection**: Searches IGDB for game information
    - 📅 **Year Information**: Adds release year to folder names
    - 🔄 **Remake Detection**: Identifies remakes and remasters
    - 💾 **Safe Renaming**: Preview before renaming
    - 🎯 **Smart Matching**: Handles multiple search variations
    - 💿 **PC Games**: Filters for PC/Windows games

    ### How to Use

    1. **Setup**: Configure your IGDB API credentials in the Setup page
    2. **Scan**: Scan your games folder to see all game folders
    3. **Process**: Process folders to get rename suggestions
    4. **Review**: Review the suggestions and rename folders

    ### Folder Naming Format

    The app renames folders to the format: `Game Name (Year)`

    **Examples:**
    - `The.Witcher.3-CODEX` → `The Witcher 3: Wild Hunt (2015)`
    - `Cyberpunk.2077.v1.5` → `Cyberpunk 2077 (2020)`
    - `HalfLife2` → `Half-Life 2 (2004)`

    ### API Credentials

    This app uses the IGDB API, which requires free credentials from Twitch:

    1. Visit [Twitch Developer Console](https://dev.twitch.tv/console/apps)
    2. Register a new application
    3. Get your Client ID and Client Secret
    4. Enter them in the Setup page

    ### Technical Details

    - **Built with**: Python
    - **API**: IGDB (Internet Game Database)
    - **Caching**: Results are cached for faster performance
    - **Platform**: Searches for PC (Windows) games only

    ### Tips

    - The app automatically tries multiple search variations to find the best match
    - Folders already in the correct format are automatically detected and skipped
    - You can always disconnect and reconfigure your settings in the Setup page
    - Settings are saved locally in `~/.game_renamer_config.yaml`

    ### Privacy & Security

    - Your API credentials are stored locally on your machine
    - No data is sent to any third party except IGDB for game searches
    - The app only renames folders - it doesn't modify game files

    ### Support

    For issues or questions, please visit the project repository on GitHub.
    """)

    st.divider()

    # Connection status
    if st.session_state.get('igdb_client'):
        st.success("✅ Currently connected to IGDB")
        if st.session_state.get('renamer'):
            st.info(f"📁 Games folder: {st.session_state.renamer.base_path}")
    else:
        st.warning("⚠️ Not connected to IGDB")
        st.info("Go to the Setup page to configure your credentials")
