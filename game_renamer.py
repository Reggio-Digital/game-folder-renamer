import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
import time

# IGDB API Constants
TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/token"
IGDB_GAMES_ENDPOINT = "https://api.igdb.com/v4/games"
IGDB_MAIN_GAME_CATEGORY = 0
IGDB_SEARCH_LIMIT = 15
IGDB_DEFAULT_PLATFORM_ID = 6  # PC/Windows as default

# Folder name patterns
ALREADY_NAMED_PATTERN = r'.+ \(\d{4}\)$'

# Default rename template
DEFAULT_RENAME_TEMPLATE = "{name} ({year})"


class TemplateFormatter:
    """Handles formatting of game folder names using customizable templates"""

    # Available template tokens and their descriptions
    AVAILABLE_TOKENS = {
        "{name}": "Game name",
        "{year}": "Release year",
        "{platform}": "Platform abbreviation",
        "{developer}": "First developer",
        "{publisher}": "First publisher",
        "{genres}": "Genres (comma-separated)",
        "{rating}": "IGDB user rating (0-10)",
        "{critic_rating}": "Critic rating (0-10)",
        "{version}": "Version title (e.g., Gold Edition)",
        "{game_modes}": "Game modes (e.g., Single player, Multiplayer)",
        "{themes}": "Game themes (comma-separated)",
        "{player_perspectives}": "Player perspectives (comma-separated)",
        "{franchise}": "Main franchise name",
        "{region}": "Release region",
        "{slug}": "URL-safe game identifier",
        "{age_rating}": "Age rating (e.g., ESRB rating)",
    }

    @staticmethod
    def format(template: str, game_data: Dict[str, Any], platform_abbreviation: str = "") -> str:
        """Format a game name using a template string

        Args:
            template: Template string with tokens like "{name} ({year})"
            game_data: Game data dictionary from IGDB API
            platform_abbreviation: Platform abbreviation (e.g., "Win", "PS4")

        Returns:
            Formatted folder name

        Example:
            >>> game_data = {"name": "The Witcher 3", "year": "2015", "developers": ["CD Projekt RED"]}
            >>> TemplateFormatter.format("{name} ({year}) [{developer}]", game_data)
            "The Witcher 3 (2015) [CD Projekt RED]"
        """
        result = template

        # Replace all tokens with their values
        replacements = {
            "{name}": game_data.get("name", "Unknown"),
            "{year}": str(game_data.get("year", "TBA")),
            "{platform}": platform_abbreviation or game_data.get("platforms", [""])[0] if game_data.get("platforms") else "",
            "{developer}": game_data.get("developers", [""])[0] if game_data.get("developers") else "",
            "{publisher}": game_data.get("publishers", [""])[0] if game_data.get("publishers") else "",
            "{genres}": ", ".join(game_data.get("genres", [])),
            "{rating}": str(game_data.get("rating", "")) if game_data.get("rating") else "",
            "{critic_rating}": str(game_data.get("aggregated_rating", "")) if game_data.get("aggregated_rating") else "",
            "{version}": game_data.get("version_title", ""),
            "{game_modes}": ", ".join(game_data.get("game_modes", [])),
            "{themes}": ", ".join(game_data.get("themes", [])),
            "{player_perspectives}": ", ".join(game_data.get("player_perspectives", [])),
            "{franchise}": game_data.get("franchise", ""),
            "{region}": game_data.get("region", ""),
            "{slug}": game_data.get("slug", ""),
            "{age_rating}": game_data.get("age_rating", ""),
        }

        for token, value in replacements.items():
            result = result.replace(token, value)

        # Clean up: remove empty brackets/parens if the content was empty
        result = re.sub(r'\[\s*\]', '', result)  # Remove empty []
        result = re.sub(r'\(\s*\)', '', result)  # Remove empty ()
        result = re.sub(r'\{\s*\}', '', result)  # Remove empty {}

        # Clean up multiple spaces and trim
        result = re.sub(r'\s+', ' ', result).strip()

        # Clean up leading/trailing separators
        result = re.sub(r'^[\s\-_]+|[\s\-_]+$', '', result)

        return result

    @staticmethod
    def get_preview(template: str, sample_game_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate a preview of what a template will look like

        Args:
            template: Template string
            sample_game_data: Optional custom sample data, uses default if not provided

        Returns:
            Preview string
        """
        if sample_game_data is None:
            sample_game_data = {
                "name": "The Witcher 3: Wild Hunt",
                "year": "2015",
                "developers": ["CD Projekt RED"],
                "publishers": ["CD Projekt"],
                "genres": ["Role-playing", "Adventure"],
                "platforms": ["Win"],
                "rating": 9.2,
                "aggregated_rating": 9.3,
                "version_title": "Complete Edition",
                "game_modes": ["Single player"],
                "themes": ["Fantasy", "Open world"],
                "player_perspectives": ["Third person"],
                "franchise": "The Witcher",
                "region": "WW",
                "slug": "the-witcher-3-wild-hunt",
                "age_rating": "M"
            }

        return TemplateFormatter.format(template, sample_game_data)

    @staticmethod
    def validate_template(template: str) -> tuple[bool, str]:
        """Validate a template string

        Args:
            template: Template string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not template or not template.strip():
            return False, "Template cannot be empty"

        # Check if template contains at least {name}
        if "{name}" not in template:
            return False, "Template must contain {name} token"

        # Check for invalid characters in folder names (Windows + Unix)
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, template.replace("{", "").replace("}", "")):
            return False, "Template contains invalid folder name characters"

        return True, ""


class IGDBClient:
    """Client for interacting with the IGDB API"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.token_expires: float = 0

    def authenticate(self) -> None:
        """Get Twitch OAuth token for IGDB API access

        Raises:
            requests.RequestException: If authentication request fails
            KeyError: If response doesn't contain expected data
        """
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        try:
            response = requests.post(TWITCH_AUTH_URL, data=auth_data, timeout=10)
            response.raise_for_status()

            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires = time.time() + data["expires_in"]
        except requests.RequestException as e:
            raise Exception(f"Authentication failed: {str(e)}")
        except KeyError as e:
            raise Exception(f"Invalid authentication response: missing {str(e)}")

    def ensure_authenticated(self) -> None:
        """Check if token is expired and refresh if needed"""
        if not self.access_token or time.time() >= self.token_expires:
            self.authenticate()

    def search_game(self, game_name: str, platform_id: Optional[int] = None) -> Dict[str, Any]:
        """Search for a game and return list of matches or single result

        Args:
            game_name: The name of the game to search for
            platform_id: IGDB platform ID to filter by (default: PC/Windows)

        Returns:
            Dictionary with status and game data:
            - single_match: {"status": "single_match", "game": {...}}
            - multiple_matches: {"status": "multiple_matches", "games": [...], "query": "..."}
            - not_found: {"status": "not_found", "query": "..."}
            - error: {"status": "error", "message": "..."}
        """
        if platform_id is None:
            platform_id = IGDB_DEFAULT_PLATFORM_ID
        try:
            self.ensure_authenticated()
        except Exception as e:
            return {"status": "error", "message": str(e)}

        search_query = self._clean_folder_name(game_name)
        search_variations = self._generate_search_variations(search_query)

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

        # Try each variation until we find a match
        games = []
        for query in search_variations:
            try:
                games = self._query_igdb(headers, query, platform_id)
                if games:
                    break  # Found some matches, stop trying variations
            except requests.RequestException:
                continue  # Try next variation

        if not games:
            return {"status": "not_found", "query": search_query}

        formatted_games = self._format_game_results(games, headers)

        if len(formatted_games) == 1:
            return {"status": "single_match", "game": formatted_games[0]}
        else:
            return {"status": "multiple_matches", "games": formatted_games, "query": search_query}

    def _query_igdb(self, headers: Dict[str, str], query: str, platform_id: int) -> List[Dict[str, Any]]:
        """Query the IGDB API for a specific search term

        Args:
            headers: Request headers with authentication
            query: Search query string
            platform_id: IGDB platform ID to filter by

        Returns:
            List of game results from IGDB

        Raises:
            requests.RequestException: If API request fails
        """
        body = f'''
            search "{query}";
            fields name, first_release_date, version_parent, version_title,
                   genres.name, involved_companies.company.name, involved_companies.developer,
                   involved_companies.publisher, rating, aggregated_rating, platforms.abbreviation,
                   game_modes.name, themes.name, player_perspectives.name, franchise.name,
                   release_dates.region, slug, age_ratings.rating;
            where category = {IGDB_MAIN_GAME_CATEGORY} & platforms = ({platform_id});
            limit {IGDB_SEARCH_LIMIT};
        '''

        response = requests.post(
            IGDB_GAMES_ENDPOINT,
            headers=headers,
            data=body,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def _generate_search_variations(self, base_name: str) -> List[str]:
        """Generate different search variations for better matching

        Args:
            base_name: The cleaned base name to generate variations from

        Returns:
            List of search query variations
        """
        search_variations = [base_name]

        # Edition patterns that might need to be removed
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
        cleaned_name = base_name
        for pattern in edition_patterns:
            match = re.search(pattern, cleaned_name)
            if match:
                cleaned_name = re.sub(pattern, '', cleaned_name).strip()
                if cleaned_name != base_name:
                    search_variations.append(cleaned_name)
                break  # Only remove one edition pattern

        # Add variation with colon (e.g., "Game Subtitle" -> "Game: Subtitle")
        if " " in cleaned_name:
            words = cleaned_name.split(" ", 1)
            if len(words) == 2:
                with_colon = f"{words[0]}: {words[1]}"
                search_variations.append(with_colon)

        return search_variations

    def _format_game_results(self, games: List[Dict[str, Any]], headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Format raw IGDB game data into standardized format

        Args:
            games: Raw game data from IGDB API
            headers: Request headers for additional API calls if needed

        Returns:
            List of formatted game dictionaries
        """
        formatted_games = []
        for game in games:
            year = self._extract_year(game.get("first_release_date"))
            is_remake = "version_parent" in game

            # Extract genres
            genres = []
            if game.get("genres"):
                genres = [g.get("name", "") for g in game["genres"] if g.get("name")]

            # Extract developers and publishers
            developers = []
            publishers = []
            if game.get("involved_companies"):
                for ic in game["involved_companies"]:
                    company = ic.get("company", {})
                    company_name = company.get("name", "")
                    if company_name:
                        if ic.get("developer"):
                            developers.append(company_name)
                        if ic.get("publisher"):
                            publishers.append(company_name)

            # Extract platform abbreviations
            platforms = []
            if game.get("platforms"):
                platforms = [p.get("abbreviation", "") for p in game["platforms"] if p.get("abbreviation")]

            # Extract ratings
            rating = game.get("rating")
            aggregated_rating = game.get("aggregated_rating")

            # Extract game modes
            game_modes = []
            if game.get("game_modes"):
                game_modes = [gm.get("name", "") for gm in game["game_modes"] if gm.get("name")]

            # Extract themes
            themes = []
            if game.get("themes"):
                themes = [t.get("name", "") for t in game["themes"] if t.get("name")]

            # Extract player perspectives
            player_perspectives = []
            if game.get("player_perspectives"):
                player_perspectives = [pp.get("name", "") for pp in game["player_perspectives"] if pp.get("name")]

            # Extract franchise
            franchise = ""
            if game.get("franchise"):
                franchise = game["franchise"].get("name", "")

            # Extract region (use first release date's region)
            region = ""
            if game.get("release_dates") and len(game["release_dates"]) > 0:
                region_code = game["release_dates"][0].get("region", "")
                # Map region codes to readable names
                region_map = {
                    1: "EU", 2: "NA", 3: "AU", 4: "NZ", 5: "JP",
                    6: "CN", 7: "AS", 8: "WW", 9: "KR", 10: "BR"
                }
                region = region_map.get(region_code, "")

            # Extract slug
            slug = game.get("slug", "")

            # Extract age rating (prefer ESRB, fallback to first available)
            age_rating = ""
            if game.get("age_ratings"):
                # Rating enum values mapped to readable strings
                esrb_ratings = {
                    6: "RP", 7: "EC", 8: "E", 9: "E10+", 10: "T", 11: "M", 12: "AO"
                }
                pegi_ratings = {
                    1: "3", 2: "7", 3: "12", 4: "16", 5: "18"
                }

                for ar in game["age_ratings"]:
                    rating_value = ar.get("rating", 0)
                    # Try ESRB first
                    if rating_value in esrb_ratings:
                        age_rating = esrb_ratings[rating_value]
                        break
                    # Fall back to PEGI
                    elif rating_value in pegi_ratings:
                        age_rating = f"PEGI {pegi_ratings[rating_value]}"

            formatted_games.append({
                "name": game["name"],
                "year": year,
                "is_remake": is_remake,
                "version_title": game.get("version_title", ""),
                "genres": genres,
                "developers": developers,
                "publishers": publishers,
                "platforms": platforms,
                "rating": round(rating / 10, 1) if rating else None,  # Convert to 0-10 scale
                "aggregated_rating": round(aggregated_rating / 10, 1) if aggregated_rating else None,
                "game_modes": game_modes,
                "themes": themes,
                "player_perspectives": player_perspectives,
                "franchise": franchise,
                "region": region,
                "slug": slug,
                "age_rating": age_rating
            })

        return formatted_games

    def _extract_year(self, timestamp: Optional[int]) -> str:
        """Extract year from Unix timestamp

        Args:
            timestamp: Unix timestamp or None

        Returns:
            Year as string or "TBA" if no timestamp
        """
        if timestamp:
            return str(datetime.fromtimestamp(timestamp).year)
        return "TBA"

    def _clean_folder_name(self, folder_name: str) -> str:
        """Clean up folder name for better search results

        Args:
            folder_name: Original folder name

        Returns:
            Cleaned folder name suitable for searching
        """
        # Remove common patterns that might interfere with search
        patterns = [
            r'-\w+$',              # Remove release group names like "-RUNE"
            r'v\d+(\.\d+)*',       # Remove version numbers like v1.0.12
            r'\([^)]*\)',          # Remove anything in parentheses
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
    """Handles renaming of game folders using IGDB data"""

    def __init__(self, igdb_client: IGDBClient, base_path: str, platform_id: Optional[int] = None):
        self.igdb_client = igdb_client
        self.base_path = base_path
        self.platform_id = platform_id if platform_id is not None else IGDB_DEFAULT_PLATFORM_ID
        self.stats = {
            'total': 0,
            'renamed': 0,
            'skipped': 0,
            'errors': 0
        }

    def get_folders(self) -> List[Dict[str, Any]]:
        """Get all folders in the base path

        Returns:
            List of folder dictionaries with name, path, and already_named status

        Raises:
            OSError: If unable to read directory
        """
        folders = []
        try:
            for folder_name in os.listdir(self.base_path):
                folder_path = os.path.join(self.base_path, folder_name)
                if os.path.isdir(folder_path):
                    # Check if already properly named
                    already_named = bool(re.match(ALREADY_NAMED_PATTERN, folder_name))
                    folders.append({
                        'name': folder_name,
                        'path': folder_path,
                        'already_named': already_named
                    })
        except OSError as e:
            raise OSError(f"Unable to read directory {self.base_path}: {str(e)}")

        return folders

    def rename_folder(self, old_name: str, new_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """Rename a single folder

        Args:
            old_name: Current folder name
            new_name: Desired folder name
            dry_run: If True, only simulate the rename without actually performing it

        Returns:
            Dictionary with success status and details
        """
        old_path = os.path.join(self.base_path, old_name)
        new_path = os.path.join(self.base_path, new_name)

        # Check if target already exists
        if os.path.exists(new_path):
            return {
                'success': False,
                'error': f'Folder "{new_name}" already exists',
                'old_name': old_name,
                'dry_run': dry_run
            }

        if dry_run:
            # Dry run mode - just simulate the rename
            return {
                'success': True,
                'old_name': old_name,
                'new_name': new_name,
                'dry_run': True
            }

        try:
            os.rename(old_path, new_path)
            return {'success': True, 'old_name': old_name, 'new_name': new_name, 'dry_run': False}
        except OSError as e:
            return {'success': False, 'error': str(e), 'old_name': old_name, 'dry_run': False}
