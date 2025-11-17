"""Utility functions for game folder renaming"""
from typing import Dict, Any, Optional


def format_game_name(game: Dict[str, Any], template: Optional[str] = None, platform_abbreviation: str = "") -> str:
    """Format a game dictionary into a display name using template

    Args:
        game: Dictionary with game data from IGDB
        template: Optional template string (uses default if not provided)
        platform_abbreviation: Platform abbreviation for the {platform} token

    Returns:
        Formatted game name according to template or default format
    """
    if template:
        from game_renamer import TemplateFormatter
        return TemplateFormatter.format(template, game, platform_abbreviation)

    # Fallback to original behavior if no template
    year = game.get('year')
    name = game.get('name', '')

    if year and year != "TBA":
        return f"{name} ({year})"
    return name


def format_game_option(game: Dict[str, Any]) -> str:
    """Format a game dictionary for display in selection dropdown

    Args:
        game: Dictionary with 'name', 'year', and 'is_remake' keys

    Returns:
        Formatted string like "Game Name (2020) [Remake/Remaster]"
    """
    base_name = format_game_name(game)
    remake_suffix = " [Remake/Remaster]" if game.get('is_remake') else ""
    return f"{base_name}{remake_suffix}"


def get_remake_badge(game: Dict[str, Any]) -> str:
    """Get a remake badge string if game is a remake/remaster

    Args:
        game: Dictionary with 'is_remake' key

    Returns:
        Badge string or empty string
    """
    return " 🔄 (Remake/Remaster)" if game.get('is_remake') else ""
