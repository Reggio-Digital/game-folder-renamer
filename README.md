# Game Folder Renamer

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red.svg)

**Transform messy game folder names into clean, organized format automatically.**

Rename folders like `Dead.Space.v1.2-RUNE` → `Dead Space (2008)` using official IGDB game database data.

> **🚀 Completely Rewritten!** This project has been fully refactored from the ground up with a modern architecture, intuitive web interface, and guided user experience. Same mission, vastly improved execution.

---

## What's New in the Refactor

This version represents a **complete rewrite** of the original CLI-based tool:

- **Modern Web Interface** - Beautiful, responsive Streamlit UI with guided navigation
- **Step-by-Step Workflow** - Clear progression through Setup → Scan → Process → Rename
- **Live Progress Tracking** - Real-time sidebar showing your progress through each step
- **Modular Architecture** - Clean separation of concerns with dedicated page modules
- **Enhanced UX** - Context-aware guidance that shows you exactly what to do next
- **Persistent State** - Session state management keeps your work safe as you navigate
- **Improved Error Handling** - Better feedback when things go wrong
- **Smart Defaults** - Intelligent configuration with saved preferences

The old CLI interface has been replaced with a fully-featured web application that's easier to use and more powerful.

---

## Overview

**Game Folder Renamer** is a specialized tool for organizing archived PC game collections stored on local drives or NAS devices. It connects to the IGDB (Internet Game Database) to fetch accurate game names and release years, then renames your folders to a clean, consistent format.

### Perfect For:
- Game archivists and collectors
- GOG backup libraries
- Steam backup folders
- Scene release collections
- Digital game archives

### What It Does:
✅ Scans your game folders and intelligently matches them with IGDB data
✅ Removes release group tags (`-RUNE`, `-CODEX`, etc.)
✅ Strips version numbers and edition labels
✅ Adds release years for chronological organization
✅ Handles multiple matches with interactive selection
✅ Caches API results for blazing-fast operations

### What It Doesn't Do:
❌ Rename installed games or active game directories
❌ Support console ROMs or non-PC platforms
❌ Modify game files (only folder names are changed)

---

## Features

### 🎨 Modern Web Interface
- **Clean, intuitive UI** built with Streamlit
- **Responsive design** works on desktop and tablet
- **Dark mode support** through Streamlit theming
- **Accessible from any browser** - no desktop app needed

### 🧭 Guided Workflow
- **Progressive navigation** - Home, Setup, Scan & Process, About
- **Context-aware guidance** - Always know what to do next
- **Live progress sidebar** - See your completion status at a glance
- **Tooltips and help text** - Inline assistance throughout

### ⚡ Smart Processing
- **Intelligent name parsing** - Handles dots, underscores, version numbers, release tags
- **Multiple search strategies** - Tries variations to maximize match rate
- **Remake/remaster detection** - Identifies remakes and labels them clearly
- **Platform filtering** - PC games only (no console clutter)
- **Result caching** - Lightning-fast repeated operations

### 💾 Persistent Configuration
- **YAML-based settings** - Saved to `~/.game_renamer_config.yaml`
- **Auto-load on startup** - Your credentials and folder path remembered
- **Easy reconfiguration** - Change settings anytime in the Setup page

### 📊 Real-Time Statistics
- **Live metrics** - Track total folders, already named, to process
- **Result categorization** - Auto-matched, needs selection, not found, errors
- **Progress tracking** - See exactly where you are in the workflow

---

## Quick Start

### Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **IGDB API Credentials** - Free from [Twitch Developer Console](https://dev.twitch.tv/console/apps)

### 1. Clone & Run

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

The startup script will:
- ✅ Verify Python 3.11+ installation
- ✅ Create virtual environment (if needed)
- ✅ Install dependencies automatically
- ✅ Launch the web app
- ✅ Open `http://localhost:8501` in your browser

### 2. Get IGDB API Credentials

1. Visit [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. Log in with Twitch (create free account if needed)
3. Click **"Register Your Application"**
4. Fill in:
   - **Name:** `Game Folder Renamer` (or anything)
   - **OAuth Redirect URLs:** `http://localhost`
   - **Category:** `Application Integration`
5. Click **"Create"** → **"Manage"**
6. Copy your **Client ID** and **Client Secret**

### 3. Configure & Go

When the app opens in your browser:

1. Click **"Setup"** in the sidebar
2. Enter your **Client ID** and **Client Secret**
3. Specify your **games folder path**
4. Check **"Save these settings"** to persist configuration
5. Click **"Connect to IGDB"**

That's it! The app will guide you through the rest.

---

## Using the App

### The Guided Workflow

The app uses a **step-by-step navigation system** that guides you through the entire process:

#### 🏠 Home
Your dashboard and command center. Shows:
- Current progress through the workflow
- Statistics on your folders and results
- Context-aware guidance on what to do next
- Quick tips and example transformations

#### 🔑 Setup
Configure your IGDB connection and settings:
- Enter API credentials (Client ID & Secret)
- Set your games folder path
- Test connection to IGDB
- Save configuration for future sessions

#### 🎮 Scan & Process
The main workspace for renaming operations:

1. **Scan Folders**
   - Click "🔍 Scan Folders" to discover all folders
   - See which are already properly named
   - View statistics on what needs processing

2. **Process Folders**
   - Click "🔄 Process All Folders" to search IGDB
   - Watch real-time progress as each folder is processed
   - Results are automatically categorized

3. **Review Results**

   Results appear in organized tabs:

   - **✅ Auto-Matched** - Single matches ready to rename
   - **🤔 Needs Selection** - Multiple games found, choose the correct one
   - **✔️ Already Renamed** - Successfully renamed folders
   - **❌ Not Found** - No match in IGDB database
   - **⚠️ Errors** - Processing errors (rare)

4. **Rename**
   - Review suggested names before applying
   - Click individual "Rename" buttons for control
   - Use "Rename All" for batch operations

#### ℹ️ About
Project information, links, and documentation.

### Understanding the Sidebar

The **Progress Sidebar** always shows your current state:

```
📋 Progress

✅ Step 1: Connected to IGDB
✅ Step 2: Scanned (142 folders)
⏳ Step 3: Process folders

────────────────────────
📁 Folder:
/mnt/games/pc-archive
```

This helps you always know where you are in the workflow.

---

## How It Works

### Name Cleaning Algorithm

The tool intelligently cleans folder names before searching:

1. **Remove release tags** - `-RUNE`, `-CODEX`, `-RELOADED`, etc.
2. **Strip version info** - `v1.2`, `v1.0.12`, etc.
3. **Remove edition labels** - `Enhanced Edition`, `GOTY`, `Complete Edition`
4. **Normalize separators** - Convert dots/underscores to spaces
5. **Handle special cases** - Roman numerals, colons, hyphens
6. **Generate variations** - Try multiple formats to maximize matches

### Search Strategy

For each folder:

1. Generate multiple search variations from cleaned name
2. Query IGDB with each variation until match found
3. Filter to PC platform only (platform ID: 6)
4. Filter to main games only (no DLC, expansions)
5. Return up to 15 results, sorted by relevance
6. Detect remakes/remasters using IGDB version data
7. Cache results to avoid redundant API calls

### Result Categorization

Results are automatically categorized:

- **Single Match** - Exactly one PC game found → ready to rename
- **Multiple Matches** - Several games found → you choose the correct one
- **Not Found** - No match in IGDB → may need manual handling
- **Error** - API or processing error → check error message

### Caching System

The app uses Streamlit's built-in caching:

- **Session state** - Persists data as you navigate between pages
- **Search results** - Cached in memory until app restart
- **Configuration** - Saved to `~/.game_renamer_config.yaml` on disk
- **Authentication tokens** - Cached for session lifetime

---

## Example Transformations

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
| `Hades.Enhanced.Edition-CODEX` | `Hades (2020)` |

---

## Configuration

### Settings File

Configuration is stored in `~/.game_renamer_config.yaml`:

```yaml
client_id: your_client_id_here
client_secret: your_client_secret_here
games_folder: /path/to/your/games
```

You can edit this file directly or use the Setup page in the app.

### Environment Customization

The app respects Streamlit configuration. Create `.streamlit/config.toml` to customize:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"

[server]
port = 8501
headless = true
```

---

## Manual Installation

If you prefer manual setup over the startup scripts:

```bash
# Clone repository
git clone https://github.com/Reggio-Digital/game-folder-renamer.git
cd game-folder-renamer

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

---

## Troubleshooting

### Port Already in Use

If port 8501 is occupied:

```bash
streamlit run app.py --server.port 8502
```

### Authentication Failed

- Verify Client ID and Client Secret are correct
- Check for extra spaces when copying credentials
- Ensure internet connection is active
- Try regenerating credentials in Twitch Developer Console

### Permission Errors

Ensure you have permissions for:
- Games folder (read/write access needed)
- Home directory (for `~/.game_renamer_config.yaml`)

### Module Not Found

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

### Games Not Found

Some games may not be in IGDB:
- Very old or obscure titles
- Newly released games (database may lag)
- Games with unusual/localized names
- Indie games not yet added

Verify the game exists at [IGDB.com](https://www.igdb.com/) before reporting an issue.

### Slow Processing

First-time processing is slower due to API calls. Subsequent operations use cached results and are much faster.

---

## Technical Details

### Architecture

```
app.py                 # Main entry point, navigation setup
├── pages_nav/
│   ├── home.py       # Dashboard with guided workflow
│   ├── setup.py      # Configuration and API setup
│   ├── process.py    # Scan, process, and rename operations
│   └── about.py      # Project information
├── game_renamer.py   # Core business logic
│   ├── IGDBClient    # API client with OAuth
│   └── GameRenamer   # Folder scanning and renaming
└── utils.py          # Shared utilities
```

### Technology Stack

- **Frontend:** Streamlit 1.29.0 web framework
- **HTTP Client:** Requests 2.31.0 for API calls
- **Config Storage:** PyYAML 6.0.1 for settings persistence
- **Authentication:** Twitch OAuth 2.0
- **API:** IGDB API v4

### API Usage

**Endpoints:**
- `https://id.twitch.tv/oauth2/token` - Authentication
- `https://api.igdb.com/v4/games` - Game search

**Query Filters:**
- Platform: PC only (ID: 6)
- Category: Main games only (ID: 0)
- Limit: 15 results per search

**Rate Limits:**
- IGDB free tier: 4 requests/second
- Caching minimizes API usage

### Dependencies

```
requests==2.31.0   # HTTP library
streamlit==1.29.0  # Web framework
PyYAML==6.0.1      # Config files
```

---

## Best Practices

### Organization Tips

- ✅ Use on **archived/backup** game folders, not active installations
- ✅ **Backup** your folders before bulk operations
- ✅ Process folders in **batches** if you have a large collection
- ✅ Carefully **review** "Needs Selection" items for accuracy
- ✅ Use **statistics** to track progress

### Version Information

Keep version info **inside** game folders, not in folder names:

**Good:**
```
Dead Space (2008)/
├── DeadSpace.exe
├── version.txt (contains "v1.2")
└── game files...
```

**Avoid:**
```
Dead Space v1.2 (2008)/
```

This keeps folder names clean while preserving version tracking.

### Collection Management

- Organize by genre in parent folders
- Use the year in folder names for chronological sorting
- Keep the tool's config file in version control for team use
- Run periodic scans to catch new additions

---

## Contributing

Contributions are welcome! Feel free to:

- 🐛 Report bugs via [GitHub Issues](https://github.com/Reggio-Digital/game-folder-renamer/issues)
- 💡 Suggest features or improvements
- 🔧 Submit pull requests
- 📖 Improve documentation

### Development Setup

```bash
# Clone and setup
git clone https://github.com/Reggio-Digital/game-folder-renamer.git
cd game-folder-renamer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run in development mode with auto-reload
streamlit run app.py

# The app will auto-reload when you edit files
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Game Data:** [IGDB (Internet Game Database)](https://www.igdb.com/)
- **Framework:** [Streamlit](https://streamlit.io/)
- **Authentication:** [Twitch Developer API](https://dev.twitch.tv/)

---

## Support & Resources

- **Issues:** [GitHub Issues](https://github.com/Reggio-Digital/game-folder-renamer/issues)
- **Documentation:** This README + in-app guidance
- **IGDB Docs:** [IGDB API Documentation](https://api-docs.igdb.com/)
- **Streamlit Docs:** [Streamlit Documentation](https://docs.streamlit.io/)

---

**Made for game collectors, archivists, and digital library enthusiasts** 🎮
