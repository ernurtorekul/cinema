"""
Service for loading and managing character pools
"""

import os
from typing import List, Dict, Any
from pathlib import Path


class CharactersService:
    """Service for loading characters from characters.txt"""

    # Character database with traits and typical roles for known names
    CHARACTER_DATABASE = {
        "tom holland": {
            "name": "Tom Holland",
            "traits": ["youthful", "energetic", "expressive", "charismatic", "relatable"],
            "style": "young, athletic build, boyish charm, expressive face",
            "typical_roles": ["young hero", "protagonist", "action hero", "friendly character"],
            "age_range": "20-30"
        },
        "murphy": {
            "name": "Murphy (Cillian Murphy)",
            "traits": ["intense", "expressive eyes", "stoic", "intelligent", "determined"],
            "style": "striking features, thin build, intense blue eyes, versatile looks",
            "typical_roles": ["brooding hero", "scientist", "complex character", "protagonist"],
            "age_range": "35-50"
        },
        "ross": {
            "name": "Ross (David Schwimmer)",
            "traits": ["nerdy", "awkward", "intelligent", "comedic", "passionate"],
            "style": "tall, curly hair, nerdy but attractive, expressive",
            "typical_roles": ["comedy relief", "nerdy character", "romantic lead", "intellectual"],
            "age_range": "35-55"
        },
        "phoebe": {
            "name": "Phoebe (Lisa Kudrow)",
            "traits": ["quirky", "eccentric", "free-spirited", "funny", "musical"],
            "style": "blonde hair, unique looks, expressive, bohemian style",
            "typical_roles": ["eccentric character", "comic relief", "free spirit", "mystical figure"],
            "age_range": "35-55"
        },
        "joey": {
            "name": "Joey (Matt LeBlanc)",
            "traits": ["charming", "simple-minded", "lovable", "food-loving", "ladies man"],
            "style": "handsome in a rugged way, muscular build, charming smile",
            "typical_roles": ["lovable fool", "romantic lead", "comic character", "action hero"],
            "age_range": "35-55"
        },
        # Additional celebrities that can be referenced
        "henry cavill": {
            "name": "Henry Cavill",
            "traits": ["strong", "charismatic", "action-hero", "intense", "commanding"],
            "style": "rugged handsome, athletic build, short dark hair, strong jawline",
            "typical_roles": ["warrior", "soldier", "leader", "hero", "action star"],
            "age_range": "30-45"
        },
        "scarlett johansson": {
            "name": "Scarlett Johansson",
            "traits": ["fierce", "intelligent", "mysterious", "confident", "strong presence"],
            "style": "striking features, versatile looks, fit physique",
            "typical_roles": ["action hero", "spy", "warrior", "enigmatic figure"],
            "age_range": "25-40"
        },
        "zendaya": {
            "name": "Zendaya",
            "traits": ["youthful", "expressive", "dynamic", "modern", "confident"],
            "style": "versatile looks, slender, striking eyes, fashionable",
            "typical_roles": ["young hero", "rebel", "modern warrior", "protagonist"],
            "age_range": "18-30"
        },
        "keanu reeves": {
            "name": "Keanu Reeves",
            "traits": ["stoic", "skilled fighter", "determined", "relatable", "cool"],
            "style": "aged but fit, calm demeanor, martial arts physique",
            "typical_roles": ["lone warrior", "assassin", "chosen one", "reluctant hero"],
            "age_range": "40-60"
        },
        "anya taylor-joy": {
            "name": "Anya Taylor-Joy",
            "traits": ["ethereal", "intense", "calculating", "mysterious", "striking"],
            "style": "striking features, blonde hair, intense gaze, slender",
            "typical_roles": ["enigmatic figure", "calculating villain", "mystical character"],
            "age_range": "20-30"
        },
        "jason momoa": {
            "name": "Jason Momoa",
            "traits": ["massive", "intimidating", "wild", "powerful", "gentle giant"],
            "style": "very tall, muscular, long hair, beard, imposing presence",
            "typical_roles": ["barbarian", "guardian", "warrior", "king"],
            "age_range": "30-50"
        },
        "margot robbie": {
            "name": "Margot Robbie",
            "traits": ["charismatic", "playful", "intense", "transformative", "versatile"],
            "style": "versatile beauty, expressive, physically fit",
            "typical_roles": ["villain", "warrior", "anti-hero", "complex character"],
            "age_range": "25-40"
        }
    }

    @classmethod
    def load_characters_from_file(cls, file_path: str = None) -> List[Dict[str, Any]]:
        """
        Load characters from characters.txt file

        Args:
            file_path: Path to characters.txt (defaults to /characters/characters.txt)

        Returns:
            List of character dictionaries with traits, roles, etc.
        """
        if file_path is None:
            # Default to characters.txt in the characters folder at project root
            # backend/app/services/characters_service.py -> go up 4 levels to reach project root
            project_root = Path(__file__).parent.parent.parent.parent
            file_path = project_root / "characters" / "characters.txt"

        characters = []

        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()

            # Parse comma-separated names
            raw_names = [name.strip() for name in content.split(',')]

            for raw_name in raw_names:
                if not raw_name:
                    continue

                # Clean up the name - remove parenthetical notes like "(from interstellar)"
                # and normalize for lookup
                display_name = raw_name
                lookup_key = raw_name.lower().strip()

                # Remove parenthetical content for lookup
                import re
                lookup_key = re.sub(r'\s*\(.*?\)\s*', '', lookup_key).strip()

                # Check if we have this character in our database
                if lookup_key in cls.CHARACTER_DATABASE:
                    characters.append(cls.CHARACTER_DATABASE[lookup_key])
                else:
                    # Create a basic entry for unknown characters
                    characters.append({
                        "name": display_name.title(),
                        "traits": ["actor", "performer"],
                        "style": "standard appearance",
                        "typical_roles": ["character", "supporting role"],
                        "age_range": "unknown"
                    })

        except FileNotFoundError:
            print(f"Characters file not found: {file_path}")
        except Exception as e:
            print(f"Error loading characters: {e}")

        return characters

    @classmethod
    def get_default_celebrity_pool(cls) -> List[Dict[str, Any]]:
        """Get the default celebrity pool as a fallback"""
        return list(cls.CHARACTER_DATABASE.values())


# Singleton instance
characters_service = CharactersService()
