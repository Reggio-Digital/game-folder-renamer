import os
import re
from datetime import datetime
import requests
import time

class IGDBClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires = 0

    def authenticate(self) -> None:
        """Get Twitch OAuth token for IGDB API access"""
        auth_url = "https://id.twitch.tv/oauth2/token"
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        response = requests.post(auth_url, data=auth_data)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires = time.time() + data["expires_in"]
        else:
            raise Exception("Authentication failed")

    def ensure_authenticated(self) -> None:
        """Check if token is expired and refresh if needed"""
        if not self.access_token or time.time() >= self.token_expires:
            self.authenticate()

    def search_game(self, game_name: str):
        """Search for a game and return list of matches or single result"""
        self.ensure_authenticated()

        # Try different variations of the name
        search_variations = []

        # Clean up the search query
        search_query = self._clean_folder_name(game_name)

        # Add base search
        search_variations.append(search_query)

        # Common edition patterns to try removing
        edition_patterns = [
            r'\s*-?\s*Enhanced Edition$',
            r'\s*-?\s*Definitive Edition$',
            r'\s*-?\s*Anniversary$',
            r'\s*-?\s*Complete Edition$',
            r'\s*-?\s*Game of the Year Edition$',
            r'\s*-?\s*GOTY Edition$',
            r'\s*-?\s*Remaster$',
            r'\s*-?\s*Remake$',
            r'\s*-?\s*Remastered$',
            r'\s*-?\s*Deluxe Edition$'
        ]

        # Try variations without edition names
        base_name = search_query
        for pattern in edition_patterns:
            cleaned_name = re.sub(pattern, '', base_name)
            if cleaned_name != base_name:
                base_name = cleaned_name
                search_variations.append(cleaned_name)

        # Add variation with colon
        if " " in base_name:
            first_word, rest = base_name.split(" ", 1)
            with_colon = f"{first_word}: {rest}"
            search_variations.append(with_colon)

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

        # Try each variation until we find a match
        for query in search_variations:
            body = f'''
                search "{query}";
                fields name, first_release_date, version_parent;
                where category = 0 & platforms = (6);
                limit 15;
            '''

            response = requests.post(
                "https://api.igdb.com/v4/games",
                headers=headers,
                data=body
            )

            if response.status_code == 200:
                games = response.json()
                if games:
                    break  # Found some matches, stop trying variations
        else:
            return {"status": "not_found", "query": search_query}

        if response.status_code == 200:
            games = response.json()
            if not games:
                return {"status": "not_found", "query": search_query}

            # Format games list
            formatted_games = []
            for game in games:
                year = datetime.fromtimestamp(game.get("first_release_date", 0)).year if game.get("first_release_date") else "TBA"
                is_remake = "version_parent" in game
                formatted_games.append({
                    "name": game["name"],
                    "year": year,
                    "is_remake": is_remake
                })

            if len(formatted_games) == 1:
                return {"status": "single_match", "game": formatted_games[0]}
            else:
                return {"status": "multiple_matches", "games": formatted_games, "query": search_query}

        return {"status": "error"}

    def _clean_folder_name(self, folder_name: str) -> str:
        """Clean up folder name for better search results"""
        # Remove common patterns that might interfere with search
        patterns = [
            r'-\w+$',  # Remove release group names like "-RUNE"
            r'v\d+(\.\d+)*',  # Remove version numbers like v1.0.12
            r'\([^)]*\)',  # Remove anything in parentheses
            r'Enhanced Edition$',  # Remove "Enhanced Edition" from the end
        ]
        
        name = folder_name
        for pattern in patterns:
            name = re.sub(pattern, '', name)
            
        # Replace dots and underscores with spaces
        name = name.replace('.', ' ').replace('_', ' ')
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name

class GameFolderRenamer:
    def __init__(self, igdb_client: IGDBClient, base_path: str):
        self.igdb_client = igdb_client
        self.base_path = base_path
        self.stats = {
            'total': 0,
            'renamed': 0,
            'skipped': 0,
            'errors': 0
        }

    def get_folders(self):
        """Get all folders in the base path"""
        folders = []
        try:
            for folder_name in os.listdir(self.base_path):
                folder_path = os.path.join(self.base_path, folder_name)
                if os.path.isdir(folder_path):
                    # Check if already properly named
                    already_named = bool(re.match(r'.+ \(\d{4}\)$', folder_name))
                    folders.append({
                        'name': folder_name,
                        'path': folder_path,
                        'already_named': already_named
                    })
        except Exception as e:
            return {'error': str(e)}
        return folders

    def rename_folder(self, old_name: str, new_name: str):
        """Rename a single folder"""
        old_path = os.path.join(self.base_path, old_name)
        new_path = os.path.join(self.base_path, new_name)

        try:
            os.rename(old_path, new_path)
            return {'success': True, 'old_name': old_name, 'new_name': new_name}
        except OSError as e:
            return {'success': False, 'error': str(e), 'old_name': old_name}