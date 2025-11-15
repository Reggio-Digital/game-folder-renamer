# Game Folder Renamer

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red.svg)

A modern web-based tool that automatically renames PC game folders with clean, consistent names using data from IGDB (Internet Game Database). Transform messy folder names like `Dead.Space.v1.2-RUNE` into properly formatted names like `Dead Space (2008)`.

## Overview

Game Folder Renamer is designed for organizing archived PC game collections (GOG downloads, Steam backups, etc.) stored on local drives or NAS devices. It provides a clean, intuitive web interface built with Streamlit that connects to IGDB's comprehensive game database to fetch accurate game names and release years.

**What it does:**
- Scans your game folders and intelligently matches them with IGDB data
- Removes release group tags, version numbers, and other clutter
- Adds release years for easy chronological organization
- Handles multiple matches with an interactive selection interface
- Caches API results for fast, efficient processing

**What it doesn't do:**
- Rename installed games or modify active game installations
- Support console ROMs or non-PC platforms
- Modify game files (only renames folders)

## Features

- **Modern Web Interface** - Clean, responsive Streamlit UI accessible from any browser
- **Smart Matching** - Intelligent name parsing with multiple search variations for accurate results
- **Persistent Configuration** - YAML-based settings storage for quick startup
- **Performance Optimized** - Built-in caching system for fast repeated operations
- **Multiple Match Handling** - Interactive selection UI when multiple games match
- **Real-time Progress** - Live progress tracking and statistics during processing
- **Remake/Remaster Detection** - Identifies and labels game remakes and remasters
- **Zero Docker** - Simple Python-based setup, no containers required

## Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **IGDB API Credentials** - Free credentials from [Twitch Developer Console](https://dev.twitch.tv/console/apps)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Reggio-Digital/game-folder-renamer.git
cd game-folder-renamer
```

### 2. Run the Application

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

The startup script will:
- Verify Python installation
- Auto-install dependencies if needed
- Launch the Streamlit app
- Open your browser to `http://localhost:8501`

### 3. Get IGDB API Credentials

1. Visit the [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. Log in with your Twitch account (create one if needed - it's free)
3. Click **"Register Your Application"**
4. Fill in the application form:
   - **Name:** Game Folder Renamer (or any name)
   - **OAuth Redirect URLs:** `http://localhost`
   - **Category:** Application Integration
5. Click **"Create"** then **"Manage"**
6. Copy your **Client ID** and **Client Secret**

### 4. Configure the Application

On first launch, you'll see a setup screen:

1. Enter your **Client ID** and **Client Secret**
2. Specify the path to your games folder
3. Check **"Save these settings for next time"** to persist your configuration
4. Click **"Connect to IGDB"**

Your settings are saved to `~/.game_renamer_config.yaml` and will be automatically loaded on subsequent runs.

## Usage Guide

### Basic Workflow

1. **Connect** - Enter API credentials and games folder path
2. **Scan** - Click "🔍 Scan Folders" to discover all game folders
3. **Process** - Click "🔄 Process All Folders" to search IGDB for matches
4. **Review** - Navigate through tabs to review results
5. **Rename** - Click rename buttons to apply changes

### Understanding the Results

Results are organized into four tabs:

#### ✅ Auto-Renamed
Single matches that are ready to rename immediately. These are high-confidence matches where IGDB found exactly one PC game matching the folder name.

#### 🤔 Needs Selection
Folders with multiple potential matches. Use the dropdown menu to select the correct game from the list. Remakes and remasters are clearly labeled.

#### ❌ Not Found
Folders that couldn't be matched in the IGDB database. These may require manual renaming or may not be in IGDB.

#### ⚠️ Errors
Folders that encountered errors during processing. Check the error messages for details.

### Statistics Dashboard

The dashboard displays:
- **Total Folders** - Number of folders found in the directory
- **Already Named** - Folders already in the correct format `Game Name (YYYY)`
- **To Process** - Folders that need to be processed
- **Processed** - Folders that have been searched in IGDB

## How It Works

### Name Cleaning Algorithm

The application intelligently cleans folder names before searching:

1. **Removes release group tags** - `-RUNE`, `-CODEX`, etc.
2. **Strips version numbers** - `v1.2`, `v1.0.12`, etc.
3. **Removes edition suffixes** - Enhanced Edition, Definitive Edition, GOTY, etc.
4. **Normalizes separators** - Converts dots and underscores to spaces
5. **Tries multiple variations** - With/without colons, different formats

### API Search Strategy

For each folder, the app:

1. Generates multiple search variations from the cleaned name
2. Queries IGDB for PC games (platform ID: 6, category: main game)
3. Returns up to 15 matches, sorted by relevance
4. Caches results to avoid redundant API calls
5. Identifies remakes/remasters using IGDB's version parent field

### Caching System

The application uses Streamlit's built-in caching:

- **Authentication tokens** - Cached for the session lifetime
- **Game searches** - Cached permanently until app restart
- **Configuration** - Persisted to YAML file on disk

## Example Transformations

```
Before                                  After
────────────────────────────────────    ─────────────────────────────────
Dead.Space.v1.2-RUNE                 →  Dead Space (2008)
Warhammer.40000.Space.Marine.2-RUNE  →  Warhammer 40000 Space Marine II (2024)
A.Plague.Tale.Innocence              →  A Plague Tale Innocence (2019)
Hades.Enhanced.Edition               →  Hades (2020)
Portal.2.GOTY                        →  Portal 2 (2011)
```

## Manual Installation

If you prefer manual setup instead of using the startup scripts:

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Configuration File

Settings are stored in `~/.game_renamer_config.yaml`:

```yaml
client_id: your_client_id_here
client_secret: your_client_secret_here
games_folder: /path/to/your/games
```

You can edit this file directly or use the in-app configuration interface.

## Troubleshooting

### Port Already in Use

If port 8501 is already in use, specify a different port:

```bash
streamlit run app.py --server.port 8502
```

### Authentication Failed

- Double-check your Client ID and Client Secret
- Ensure there are no extra spaces when copying credentials
- Try regenerating credentials from the Twitch Developer Console
- Verify your internet connection

### Permission Errors

Ensure you have read/write permissions for:
- The games folder you're trying to rename
- Your home directory (for storing `~/.game_renamer_config.yaml`)

### Module Not Found

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Games Not Found in IGDB

Some games may not be in the IGDB database, particularly:
- Very old or obscure games
- Newly released games (database may lag by a few days)
- Games with unusual or localized names

Try searching IGDB manually to verify if the game exists in their database.

## Technical Details

### Architecture

- **Frontend:** Streamlit web framework
- **API Client:** Custom IGDB wrapper with OAuth 2.0 authentication
- **Data Storage:** YAML configuration files
- **Caching:** Streamlit's `@st.cache_resource` and `@st.cache_data`

### API Usage

The application uses IGDB API v4 with the following endpoints:
- **Authentication:** Twitch OAuth 2.0 token endpoint
- **Search:** IGDB games endpoint with search and filtering

API queries are filtered to:
- **Platform:** PC only (platform ID: 6)
- **Category:** Main games only (category: 0)
- **Limit:** 15 results per search

### Dependencies

- **streamlit** - Web framework for the UI
- **requests** - HTTP library for API calls
- **PyYAML** - YAML configuration file handling

## Best Practices

### Version Information

Keep version numbers inside game folders rather than in folder names:

```
Good:
Dead Space (2008)/
├── Dead Space v1.2.exe
├── version.txt
└── game files...

Avoid:
Dead Space v1.2 (2008)/
```

This maintains clean, consistent folder names while preserving version information where it belongs.

### Backup First

Always keep a backup of your game folders before running bulk rename operations. While the tool is designed to be safe, having a backup provides peace of mind.

### Organization Tips

- Use the tool on archived/backup game folders, not active installations
- Process folders in batches if you have a large collection
- Review "Needs Selection" items carefully to ensure correct game selection
- Use the statistics dashboard to track your progress

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Reggio-Digital/game-folder-renamer.git
cd game-folder-renamer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run app.py
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Game data provided by [IGDB](https://www.igdb.com/)
- Built with [Streamlit](https://streamlit.io/)
- Authentication via [Twitch Developer API](https://dev.twitch.tv/)

## Support

- **Issues:** [GitHub Issues](https://github.com/Reggio-Digital/game-folder-renamer/issues)
- **Documentation:** This README and in-app help tooltips
- **IGDB API:** [IGDB API Documentation](https://api-docs.igdb.com/)

---

Made with ❤️ for game collectors and digital archivists
