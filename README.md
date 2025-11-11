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
- 🐳 Runs in Docker for easy deployment on any system

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

- Docker and Docker Compose installed on your system
  - [Install Docker for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Install Docker for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - [Install Docker for Linux](https://docs.docker.com/engine/install/)
- IGDB API credentials (free)
  - Sign up at [IGDB](https://api.igdb.com)
  - Create a Twitch application to get your credentials

## Setup

1. Clone this repository or download the files:
   ```bash
   git clone https://github.com/yourusername/game-folder-renamer.git
   cd game-folder-renamer
   ```

2. Get your IGDB API credentials:
   - Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps)
   - Create a new application
   - Note down your Client ID and Client Secret

3. Edit the `docker-compose.yml` file to configure your settings:
   ```yaml
   services:
     game-renamer:
       image: game-renamer
       build: .
       ports:
         - "8501:8501"
       environment:
         - IGDB_CLIENT_ID=your_client_id_here
         - IGDB_CLIENT_SECRET=your_client_secret_here
         - GAMES_FOLDER=/games
       volumes:
         - "/path/to/your/games:/games"  # Update this path
   ```

4. Build and start the container:
   ```bash
   docker-compose up --build
   ```

5. Open your web browser and navigate to:
   ```
   http://localhost:8501
   ```

## Usage

### Web Interface

1. **Configure Credentials**:
   - If you didn't set them in docker-compose.yml, enter your IGDB Client ID and Client Secret in the sidebar
   - Specify the games folder path (default: `/games`)

2. **Connect to IGDB**:
   - Click the "🔌 Connect to IGDB" button in the sidebar
   - Wait for successful authentication

3. **Scan Folders**:
   - Click "🔍 Scan Folders" to see all game folders in your directory
   - View statistics about total folders, already named folders, and folders to process

4. **Process Folders**:
   - Click "🔄 Process All Folders" to search IGDB for all games
   - The app will automatically search for each folder and categorize results

5. **Review and Rename**:
   - **Auto-Renamed Tab**: Single matches that are ready to rename
   - **Needs Selection Tab**: Multiple matches requiring your selection
   - **Not Found Tab**: Folders that couldn't be found in IGDB
   - **Errors Tab**: Any folders that encountered errors

6. **Apply Changes**:
   - Review each suggestion
   - Click "✅ Rename" to apply the change
   - For multiple matches, select the correct game and click "✅ Apply"

### Running Without Docker Compose

You can also run the container directly:

```bash
docker build -t game-renamer .

docker run -p 8501:8501 \
  -e IGDB_CLIENT_ID=your_id \
  -e IGDB_CLIENT_SECRET=your_secret \
  -e GAMES_FOLDER=/games \
  -v "/path/to/games:/games" \
  game-renamer
```

Then open http://localhost:8501 in your browser.

### Local Development (Without Docker)

If you want to run the app locally without Docker:

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export IGDB_CLIENT_ID=your_id
   export IGDB_CLIENT_SECRET=your_secret
   export GAMES_FOLDER=/path/to/games
   ```

3. Run Streamlit:
   ```bash
   streamlit run app.py
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

### Statistics Dashboard
- Total folders found
- Already properly named folders
- Folders needing processing
- Processed folders count

## Troubleshooting

### Port Already in Use
If port 8501 is already in use, you can change it in docker-compose.yml:
```yaml
ports:
  - "8502:8501"  # Use port 8502 instead
```

### Can't Access Folders
Make sure the volume mount path is correct and the Docker container has permission to access the folders.

### Authentication Failed
Double-check your IGDB Client ID and Client Secret. You may need to regenerate them from the Twitch Developer Console.

## License

MIT License - Feel free to use and modify as needed.
