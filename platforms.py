"""IGDB Platform utilities - fetch and match platforms dynamically from API"""
import os
from typing import Dict, List, Optional, Tuple
import requests
import streamlit as st


# Streamlit cache decorator for platform fetching
@st.cache_data(ttl=None)  # Cache forever since platforms rarely change
def _fetch_platforms_cached(client_id: str, access_token: str) -> List[Dict]:
    """Cached wrapper for fetching platforms from IGDB API

    Args:
        client_id: IGDB client ID
        access_token: IGDB access token

    Returns:
        List of platform dictionaries
    """
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }

    body = """
        fields id, name, slug, abbreviation, alternative_name, platform_family, platform_logo.image_id;
        limit 500;
        sort name asc;
    """

    try:
        response = requests.post(
            "https://api.igdb.com/v4/platforms",
            headers=headers,
            data=body,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch platforms: {str(e)}")


class PlatformManager:
    """Manages platform data from IGDB API"""

    def __init__(self, client_id: str, access_token: str):
        self.client_id = client_id
        self.access_token = access_token

    def fetch_all_platforms(self) -> List[Dict]:
        """Fetch all platforms from IGDB API (cached)

        Returns:
            List of platform dictionaries with id, name, slug, abbreviation, etc.
        """
        return _fetch_platforms_cached(self.client_id, self.access_token)

    def match_folder_to_platform(self, folder_name: str) -> Optional[Dict]:
        """Match a folder name to a platform (case-insensitive exact match)

        Matching priority:
        1. abbreviation (e.g., "PS4", "Win")
        2. slug (e.g., "ps4", "win")
        3. name (e.g., "PlayStation 4", "Windows")
        4. alternative_name (e.g., "PC")

        Args:
            folder_name: The folder name to match (e.g., "Win", "win", "PS4", "ps4")

        Returns:
            Platform dict if exact match found, None otherwise
        """
        platforms = self.fetch_all_platforms()
        folder_lower = folder_name.lower()

        for platform in platforms:
            # Priority 1: Match abbreviation (most common - "PS4", "Win")
            if platform.get('abbreviation') and platform['abbreviation'].lower() == folder_lower:
                return platform

            # Priority 2: Match slug (url-safe name - "ps4", "win")
            if platform.get('slug') and platform['slug'].lower() == folder_lower:
                return platform

            # Priority 3: Match full name (less common - "PlayStation 4", "Windows")
            if platform.get('name') and platform['name'].lower() == folder_lower:
                return platform

            # Priority 4: Match alternative name (e.g., "PC" for Windows)
            if platform.get('alternative_name') and platform['alternative_name'].lower() == folder_lower:
                return platform

        return None

    def detect_platform_folders(self, base_path: str) -> List[Tuple[str, int, str]]:
        """Scan a directory for platform-specific subfolders

        Args:
            base_path: The base directory to scan

        Returns:
            List of (folder_name, platform_id, platform_name) tuples sorted by platform name
        """
        detected = []

        if not os.path.exists(base_path) or not os.path.isdir(base_path):
            return detected

        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)
            if os.path.isdir(folder_path):
                platform = self.match_folder_to_platform(folder_name)
                if platform:
                    detected.append((
                        folder_name,
                        platform['id'],
                        platform['name']
                    ))

        return sorted(detected, key=lambda x: x[2])

    def get_platform_display_name(self, platform: Dict) -> str:
        """Get a formatted display name for a platform

        Args:
            platform: Platform dictionary from API

        Returns:
            Formatted string like "PlayStation 4 (PS4)" or just "Windows"
        """
        name = platform.get('name', 'Unknown')
        abbr = platform.get('abbreviation')

        if abbr and abbr.lower() != name.lower():
            return f"{name} ({abbr})"
        return name

    def get_platform_choices(self) -> List[Tuple[int, str]]:
        """Get all platforms formatted for UI selection dropdown

        Returns:
            List of (platform_id, display_name) tuples sorted by name
        """
        platforms = self.fetch_all_platforms()
        choices = []

        for platform in platforms:
            display = self.get_platform_display_name(platform)
            choices.append((platform['id'], display))

        return choices
