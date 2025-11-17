# Game Folder Renamer

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red.svg)

A web-based tool for automatically renaming PC game folders using the IGDB database. Transforms messy folder names like `Dead.Space.v1.2-RUNE` into clean, organized names like `Dead Space (2008)`.

> **Note:** This project has been completely refactored from the original CLI version. It now features a web interface built with Streamlit and a modular architecture. Same purpose, much better implementation.
>
> **Development Status:** This project is currently in active development and may see frequent changes. While the tool is functional, it's not yet 100% stable. We're working toward a v1.0 release that will provide a stable version for users while development continues. For now, expect updates and potential breaking changes as we improve the codebase.

## Overview

This tool is designed for organizing archived PC game collections (GOG downloads, Steam backups, scene releases) stored on local drives or NAS devices. It queries the IGDB API to get accurate game names and release years, then renames your folders accordingly.

**What it does:**
- Scans game folders and matches them against IGDB
- Removes release group tags, version numbers, and edition suffixes
- Adds release years for chronological sorting
- Handles multiple matches with a selection interface
- Caches results to minimize API calls

**What it doesn't do:**
- Modify installed games or active installations
- Support console ROMs or non-PC platforms
- Touch any files inside folders (only renames the folders themselves)

## Features

### Web Interface
The refactored version replaces the CLI with a Streamlit web app featuring:
- Multi-page navigation (Home, Setup, Scan & Process, About)
- Progress tracking sidebar
- Live statistics and result categorization
- Session state persistence across page changes

### Smart Matching
- Intelligent name parsing removes common patterns (dots, underscores, release tags)
- Multiple search variations per folder to maximize matches
- Filters for PC platform and main games only (no DLC/expansions)
- Remake/remaster detection using IGDB version data

### Configuration
- YAML-based settings stored in `~/.game_renamer_config.yaml`
- API credentials and folder path auto-load on startup
- In-app configuration interface

## Installation

### Quick Start

The repository includes startup scripts that handle everything automatically:

**Linux/Mac:**
```bash
git clone https://github.com/Reggio-Digital/game-folder-renamer.git
cd game-folder-renamer
./run.sh
```

**Windows:**
```cmd
git clone https://github.com/Reggio-Digital/game-folder-renamer.git
cd game-folder-renamer
run.bat
```

The script will:
- Check for Python 3.11+
- Create a virtual environment if needed
- Install dependencies
- Launch the app at `http://localhost:8501`

### Manual Installation

If you prefer to set it up manually:

```bash
git clone https://github.com/Reggio-Digital/game-folder-renamer.git
cd game-folder-renamer

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Getting IGDB API Credentials

You'll need free API credentials from Twitch:

1. Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. Log in (create account if needed)
3. Click "Register Your Application"
4. Fill in:
   - Name: anything you want
   - OAuth Redirect URLs: `http://localhost`
   - Category: Application Integration
5. Click "Create" then "Manage"
6. Copy your Client ID and Client Secret

## Usage

### Initial Setup

1. Launch the app (it opens in your browser automatically)
2. Go to the Setup page in the sidebar
3. Enter your Client ID and Client Secret
4. Specify your games folder path
5. Check "Save these settings" to persist your config
6. Click "Connect to IGDB"

Your settings are saved to `~/.game_renamer_config.yaml` and will auto-load next time.

### Basic Workflow

The app guides you through a three-step process:

**Step 1: Connect**
- Configure API credentials and games folder path
- Test connection to IGDB

**Step 2: Scan**
- Click "Scan Folders" to discover all folders in your games directory
- See which folders are already properly named
- View statistics on what needs processing

**Step 3: Process**
- Click "Process All Folders" to search IGDB for each folder
- Results are automatically categorized into tabs:
  - **Auto-Matched:** Single matches ready to rename
  - **Needs Selection:** Multiple games found, choose the correct one
  - **Already Renamed:** Successfully renamed folders
  - **Not Found:** No match in IGDB database
  - **Errors:** Processing errors (if any)

**Step 4: Rename**
- Review the suggested names
- Click individual "Rename" buttons or use "Rename All"
- Folders are renamed in place

### Progress Tracking

The sidebar shows your current state:
- Step 1: Connection status
- Step 2: Scan status (with folder count)
- Step 3: Process status (with result count)
- Current games folder path

## How It Works

### Name Cleaning

Before searching IGDB, the tool cleans folder names:

1. Remove release group tags (`-RUNE`, `-CODEX`, `-RELOADED`, etc.)
2. Strip version numbers (`v1.2`, `v1.0.12`, etc.)
3. Remove edition suffixes (`Enhanced Edition`, `GOTY`, `Complete Edition`)
4. Normalize separators (dots and underscores to spaces)
5. Handle special cases (roman numerals, colons, hyphens)

### Search Strategy

For each folder:
1. Generate multiple search variations from the cleaned name
2. Query IGDB with each variation until a match is found
3. Filter results to PC platform only (platform ID: 6)
4. Filter to main games only (category: 0, no DLC/expansions)
5. Return up to 15 matches sorted by relevance
6. Identify remakes/remasters using IGDB's version parent field
7. Cache results to avoid redundant API calls

### Result Categories

- **Single Match:** Exactly one game found, ready to rename immediately
- **Multiple Matches:** Several games found, user selects the correct one
- **Not Found:** No match in IGDB (very old/obscure games, or not in database yet)
- **Error:** API error or processing issue

## Examples

| Before | After |
|--------|-------|
| `Dead.Space.v1.2-RUNE` | `Dead Space (2008)` |
| `Warhammer.40000.Space.Marine.2-RUNE` | `Warhammer 40000: Space Marine II (2024)` |
| `Cyberpunk.2077.v1.5-CODEX` | `Cyberpunk 2077 (2020)` |
| `The.Witcher.3.Wild.Hunt.GOTY` | `The Witcher 3: Wild Hunt (2015)` |
| `HalfLife2` | `Half-Life 2 (2004)` |
| `GTA.V-RELOADED` | `Grand Theft Auto V (2015)` |
| `Portal.2.Enhanced.Edition` | `Portal 2 (2011)` |
| `A.Plague.Tale.Innocence` | `A Plague Tale: Innocence (2019)` |

## Configuration

### Settings File

Configuration is stored in `~/.game_renamer_config.yaml`:

```yaml
client_id: your_client_id_here
client_secret: your_client_secret_here
games_folder: /path/to/your/games
```

You can edit this file directly or use the Setup page.

### Streamlit Customization

Create `.streamlit/config.toml` to customize the interface:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"

[server]
port = 8501
headless = true
```

## Architecture

The refactored codebase is organized as follows:

```
app.py                 # Main entry point, navigation setup, session state
├── pages_nav/
│   ├── home.py       # Dashboard with progress tracking
│   ├── setup.py      # API configuration
│   ├── process.py    # Scan, process, and rename operations
│   └── about.py      # Project information
├── game_renamer.py   # Core business logic
│   ├── IGDBClient    # API client with OAuth 2.0
│   └── GameRenamer   # Folder scanning and renaming
└── utils.py          # Shared utilities
```

### Technology Stack

- **Streamlit 1.29.0** - Web framework
- **Requests 2.31.0** - HTTP client for API calls
- **PyYAML 6.0.1** - Configuration file handling
- **IGDB API v4** - Game database
- **Twitch OAuth 2.0** - Authentication

### API Details

**Endpoints:**
- `https://id.twitch.tv/oauth2/token` - OAuth token
- `https://api.igdb.com/v4/games` - Game search

**Query Filters:**
- Platform: PC only (ID: 6)
- Category: Main games (ID: 0)
- Limit: 15 results per search

**Rate Limits:**
- 4 requests/second (free tier)
- Caching minimizes API usage

## Troubleshooting

### Port Already in Use

```bash
streamlit run app.py --server.port 8502
```

### Authentication Failed

- Double-check Client ID and Client Secret
- Remove any extra spaces when copying
- Verify internet connection
- Try regenerating credentials

### Permission Errors

Ensure you have read/write permissions for:
- The games folder you're renaming
- Your home directory (for config file)

### Games Not Found

Some games may not be in IGDB:
- Very old or obscure titles
- Newly released games (database lag)
- Indie games not yet added
- Non-English or localized names

Check if the game exists on [IGDB.com](https://www.igdb.com/) first.

### Slow Processing

First-time processing requires API calls. Subsequent operations use cached results and are much faster.

## Best Practices

### Backup First

Always backup your game folders before running bulk rename operations. The tool is safe but backups are good practice.

### Use on Archives

This tool is meant for archived/backup game folders, not active installations or game directories that launchers are pointing to.

### Version Numbers

Keep version info inside game folders, not in folder names:

**Good:**
```
Dead Space (2008)/
├── DeadSpace.exe
├── version.txt
└── ...
```

**Avoid:**
```
Dead Space v1.2 (2008)/
```

### Batch Processing

If you have a large collection, process folders in batches and review results carefully, especially the "Needs Selection" items.

## Contributing

Contributions welcome. Feel free to:
- Report bugs via GitHub Issues
- Submit pull requests
- Suggest improvements

### Development Setup

```bash
git clone https://github.com/Reggio-Digital/game-folder-renamer.git
cd game-folder-renamer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py  # Auto-reloads on file changes
```

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Game data from [IGDB](https://www.igdb.com/)
- Built with [Streamlit](https://streamlit.io/)
- Authentication via [Twitch Developer API](https://dev.twitch.tv/)

---

Made with ❤️ for game collectors and digital archivists
