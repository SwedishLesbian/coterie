"""Utility for loading game data from JSON files."""

import json
import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

class DataLoader:
    """Utility for loading and caching game data from JSON files."""
    
    # Cache for loaded data
    _data_cache: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def get_data_path(cls, file_name: str) -> str:
        """Get the full path to a data file.
        
        Args:
            file_name: Name of the file (with or without .json extension)
            
        Returns:
            Full path to the file
        """
        # Ensure the file has .json extension
        if not file_name.endswith('.json'):
            file_name += '.json'
            
        # Get the path to the data directory
        base_dir = Path(__file__).resolve().parent.parent.parent
        data_dir = base_dir / 'data'
        
        return str(data_dir / file_name)
    
    @classmethod
    def load_data(cls, file_name: str, force_reload: bool = False) -> Dict[str, Any]:
        """Load data from a JSON file.
        
        Args:
            file_name: Name of the file (with or without .json extension)
            force_reload: Whether to force reload from disk even if cached
            
        Returns:
            Dictionary of loaded data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        # Ensure the file has .json extension
        if not file_name.endswith('.json'):
            file_name += '.json'
            
        # Check cache first
        if file_name in cls._data_cache and not force_reload:
            return cls._data_cache[file_name]
            
        # Get the full path
        file_path = cls.get_data_path(file_name)
        
        # Load the data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Cache the data
        cls._data_cache[file_name] = data
        
        return data
    
    @classmethod
    def get_category(cls, file_name: str, category: str) -> List[str]:
        """Get a list of items from a category in a data file.
        
        Args:
            file_name: Name of the file
            category: Category name
            
        Returns:
            List of items in the category
            
        Raises:
            KeyError: If the category doesn't exist
        """
        data = cls.load_data(file_name)
        
        if category not in data:
            raise KeyError(f"Category '{category}' not found in {file_name}")
            
        return data[category]
    
    @classmethod
    def get_descriptions(cls, file_name: str) -> Dict[str, str]:
        """Get descriptions from a data file.
        
        Args:
            file_name: Name of the file
            
        Returns:
            Dictionary of item names to descriptions
            
        Raises:
            KeyError: If the descriptions category doesn't exist
        """
        data = cls.load_data(file_name)
        
        if "descriptions" not in data:
            return {}
            
        return data["descriptions"]
    
    @classmethod
    def get_item_description(cls, file_name: str, item_name: str) -> str:
        """Get the description of a specific item.
        
        Args:
            file_name: Name of the file
            item_name: Name of the item
            
        Returns:
            Description of the item or empty string if not found
        """
        try:
            descriptions = cls.get_descriptions(file_name)
            return descriptions.get(item_name, "")
        except (KeyError, FileNotFoundError):
            return ""
            
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the data cache."""
        cls._data_cache.clear()
    
    @classmethod
    def parse_gv3_character(cls, file_path: str) -> Dict[str, Any]:
        """Parse a Grapevine 3 character file (.gvc).
        
        Args:
            file_path: Path to the .gvc file
            
        Returns:
            Dictionary containing character data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid GV3 character file
        """
        # Basic character data structure
        character = {
            "name": "",
            "player": "",
            "chronicle": "",
            "nature": "",
            "demeanor": "",
            "concept": "",
            "clan": "",
            "generation": 0,
            "type": "Unknown",
            "attributes": {},
            "abilities": {},
            "disciplines": {},
            "backgrounds": {},
            "virtues": {},
            "merits": [],
            "flaws": [],
            "notes": "",
            "source_file": file_path,
            "source_format": "gv3"
        }
        
        try:
            # GV3 files are text-based with specific markers
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
                
            # Extract character type from file path or content
            if "vampire" in file_path.lower():
                character["type"] = "Vampire"
            elif "werewolf" in file_path.lower():
                character["type"] = "Werewolf"
            elif "mage" in file_path.lower():
                character["type"] = "Mage"
            
            # Extract basic info
            name_match = re.search(r"Name\s*:\s*([^\r\n]+)", content)
            if name_match:
                character["name"] = name_match.group(1).strip()
                
            player_match = re.search(r"Player\s*:\s*([^\r\n]+)", content)
            if player_match:
                character["player"] = player_match.group(1).strip()
                
            # Extract additional data based on character type
            # This is a simplified implementation - a full parser would be more complex
            if character["type"] == "Vampire":
                clan_match = re.search(r"Clan\s*:\s*([^\r\n]+)", content)
                if clan_match:
                    character["clan"] = clan_match.group(1).strip()
                    
                gen_match = re.search(r"Generation\s*:\s*(\d+)", content)
                if gen_match:
                    character["generation"] = int(gen_match.group(1))
                    
            # TODO: Add more detailed parsing for traits, disciplines, etc.
            
            return character
            
        except Exception as e:
            raise ValueError(f"Failed to parse GV3 file: {str(e)}")
    
    @classmethod
    def parse_gex_character(cls, file_path: str) -> Dict[str, Any]:
        """Parse a Grapevine exported character file (.gex).
        
        Args:
            file_path: Path to the .gex file
            
        Returns:
            Dictionary containing character data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid GEX file
        """
        # Basic character data structure
        character = {
            "name": "",
            "player": "",
            "chronicle": "",
            "nature": "",
            "demeanor": "",
            "concept": "",
            "clan": "",
            "generation": 0,
            "type": "Unknown",
            "attributes": {},
            "abilities": {},
            "disciplines": {},
            "backgrounds": {},
            "virtues": {},
            "merits": [],
            "flaws": [],
            "notes": "",
            "source_file": file_path,
            "source_format": "gex"
        }
        
        try:
            # GEX files are XML-based
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check if this is a valid GEX file
            if root.tag != "grapevine_character":
                raise ValueError("Not a valid GEX file")
                
            # Extract basic info
            basic_info = root.find("basic_info")
            if basic_info is not None:
                name_elem = basic_info.find("name")
                if name_elem is not None:
                    character["name"] = name_elem.text or ""
                    
                player_elem = basic_info.find("player")
                if player_elem is not None:
                    character["player"] = player_elem.text or ""
                    
                chronicle_elem = basic_info.find("chronicle")
                if chronicle_elem is not None:
                    character["chronicle"] = chronicle_elem.text or ""
                    
                # Determine character type
                template_elem = root.find("template")
                if template_elem is not None:
                    type_elem = template_elem.find("type")
                    if type_elem is not None:
                        character["type"] = type_elem.text or "Unknown"
                        
                    # Extract type-specific info
                    if character["type"] == "Vampire":
                        clan_elem = template_elem.find("clan")
                        if clan_elem is not None:
                            character["clan"] = clan_elem.text or ""
                            
                        gen_elem = template_elem.find("generation")
                        if gen_elem is not None and gen_elem.text:
                            try:
                                character["generation"] = int(gen_elem.text)
                            except ValueError:
                                pass
                
            # TODO: Add more detailed parsing for traits, disciplines, etc.
            
            return character
            
        except ET.ParseError:
            raise ValueError("Invalid XML in GEX file")
        except Exception as e:
            raise ValueError(f"Failed to parse GEX file: {str(e)}")
    
    @classmethod
    def extract_character_info(cls, file_path: str) -> Tuple[Dict[str, Any], str]:
        """Extract basic character info from a file, detecting the format.
        
        Args:
            file_path: Path to the character file
            
        Returns:
            Tuple of (character data dictionary, file format)
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Determine file type based on extension
        if file_path.lower().endswith('.gvc'):
            return cls.parse_gv3_character(file_path), "gv3"
        elif file_path.lower().endswith('.gex'):
            return cls.parse_gex_character(file_path), "gex"
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
            
    @classmethod
    def import_character(cls, file_path: str, target_dir: Optional[str] = None) -> str:
        """Import a character from a GV3 or GEX file and save it to the Coterie format.
        
        Args:
            file_path: Path to the character file
            target_dir: Optional directory to save the character to
            
        Returns:
            Path to the imported character file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        # Extract character data and format
        character_data, format_type = cls.extract_character_info(file_path)
        
        # If no target directory specified, use the default character directory
        if target_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            target_dir = base_dir / 'characters'
            
            # Create directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)
        
        # Generate filename based on character name
        safe_name = re.sub(r'[^\w\-_.]', '_', character_data["name"] or "unnamed")
        target_file = os.path.join(target_dir, f"{safe_name}.json")
        
        # Save character data
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=2)
            
        return target_file 