# Game Folder Renamer

A web-based tool built with Streamlit that automatically renames your PC game folders using IGDB.com data. It adds release years and cleans up folder names, transforming folders like `Dead.Space-RUNE` into `Dead Space (2008)`.

> **Note**: This tool is designed for organizing archived PC game folders (like GOG downloads stored on a NAS) and not for renaming installed games. It's perfect for cleaning up your PC game backup folders, ensuring consistent naming across your collection.

> **Important**: This tool is specifically for PC games only. It does not support console ROMs, Mac games, or other platforms.

## Features

- 🎮 Web-based Streamlit interface for easy interaction
- 🔍 Automatically fetches correct game names and release years from IGDB
- 🎯 Handles multiple matches with an intuitive selection UI
- 🧹 Cleans up release group names and version numbers for consistent naming
- 📊 Real-time progress tracking and statistics
- ⚡ Simple setup - no Docker required

## Use Case

This tool is ideal for scenarios like:
- Organizing PC game downloads (GOG, Steam backups, etc.) in your backup storage
- Maintaining a clean game archive on your NAS
- Standardizing folder names in your game collection

It is **not** intended for:
- Renaming installed games
- Modifying game installation directories
- Renaming active game folders
- Console ROMs or emulator games
- Mac or other non-PC platforms

## Prerequisites

- Python 3.11 or higher
- IGDB API credentials (free)
  - Sign up at [IGDB](https://api.igdb.com)
  - Create a Twitch application to get your credentials

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/game-folder-renamer.git
   cd game-folder-renamer
   ```

2. Get your IGDB API credentials:
   - Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps)
   - Create a new application
   - Note down your Client ID and Client Secret

## Usage

### Quick Start (Recommended)

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```bash
run.bat
```

The startup script will:
- Check if Python is installed
- Automatically install dependencies if needed
- Start the Streamlit app
- Open your browser to http://localhost:8501

### Manual Start

If you prefer to run manually:

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

### Using the Web Interface

Once the app is running:

1. **Configure Credentials**: Enter your IGDB Client ID and Client Secret in the sidebar
2. **Specify Folder Path**: Enter the path to your games folder
3. **Connect to IGDB**: Click the "🔌 Connect to IGDB" button
4. **Scan Folders**: Click "🔍 Scan Folders" to see all game folders
5. **Process Folders**: Click "🔄 Process All Folders" to search IGDB for all games
6. **Review and Rename**: Navigate through tabs to review and rename folders

### Environment Variables (Optional)

You can set environment variables to pre-fill the configuration:

**Linux/Mac:**
```bash
export IGDB_CLIENT_ID=your_client_id_here
export IGDB_CLIENT_SECRET=your_client_secret_here
export GAMES_FOLDER=/path/to/your/games
./run.sh
```

**Windows:**
```cmd
set IGDB_CLIENT_ID=your_client_id_here
set IGDB_CLIENT_SECRET=your_client_secret_here
set GAMES_FOLDER=C:\path\to\your\games
run.bat
```

## How It Works

1. The app scans the specified games folder via the web interface
2. For each folder:
   - Cleans up the name for searching
   - Queries IGDB for matching PC games
   - Displays results in the web interface
3. Single matches are shown in the "Auto-Renamed" tab
4. Multiple matches are shown in the "Needs Selection" tab where you can choose the correct game
5. Click to rename folders with the correct name and release year

## Interface Overview

### Tabs

- **✅ Auto-Renamed**: Single matches that are ready to rename with one click
- **🤔 Needs Selection**: Multiple matches requiring your selection from a dropdown
- **❌ Not Found**: Folders that couldn't be found in IGDB
- **⚠️ Errors**: Any folders that encountered errors

### Statistics Dashboard

- Total folders found
- Already properly named folders
- Folders needing processing
- Processed folders count

## Version Numbers

For better organization, it's recommended to keep version information inside the game folder rather than in the folder name. For example:

```
Dead Space (2008)/
├── Dead Space v1.2.exe
├── version.txt
└── ...
```

This keeps the main folder names clean and consistent while maintaining version information where it belongs - with the game files themselves.

## Example Transformations

```
Before                          After
-------                         -----
Dead.Space.v1.2              → Dead Space (2008)
Warhammer.40000.SM.2-RUNE    → Warhammer 40000 Space Marine II (2024)
A.Plague.Tale.Innocence      → A Plague Tale Innocence (2019)
```

## Features in Detail

### Smart Name Matching
- Removes common edition suffixes (Enhanced, Definitive, GOTY, etc.)
- Tries multiple search variations (with/without colons, etc.)
- Handles release groups and version numbers

### Remake/Remaster Detection
- Identifies remakes and remasters
- Shows badges to help distinguish versions
- Allows you to choose between original and remake releases

## Troubleshooting

### Port Already in Use
If port 8501 is already in use, you can specify a different port:
```bash
streamlit run app.py --server.port 8502
```

### Can't Access Folders
Make sure you have read/write permissions for the games folder path you specify.

### Authentication Failed
Double-check your IGDB Client ID and Client Secret. You may need to regenerate them from the Twitch Developer Console.

### Module Not Found
Make sure you've installed all requirements:
```bash
pip install -r requirements.txt
```

## License

MIT License - Feel free to use and modify as needed.
