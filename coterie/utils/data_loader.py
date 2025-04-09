"""Utility for loading game data from JSON files."""

import json
import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

# Add import for the trait converter
from coterie.utils.trait_converter import TraitConverter
from coterie.models.larp_trait import LarpTrait, TraitCategory
from coterie.database.engine import get_session
from coterie.models.base import Trait, Character
from coterie.models.vampire import Vampire

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

    @staticmethod
    def load_grapevine_file(file_path: str) -> Dict:
        """Load a Grapevine character file (.gvc or .gex).
        
        Args:
            file_path: Path to the Grapevine file
            
        Returns:
            Dictionary containing character data
        """
        # Check file extension to determine type
        if file_path.lower().endswith('.gex'):
            return DataLoader.load_grapevine_xml(file_path)
        else:
            return DataLoader.load_grapevine_data(file_path)
    
    @staticmethod
    def load_grapevine_data(file_path: str) -> Dict:
        """Load data from a Grapevine 3.x character file (.gvc).
        
        Args:
            file_path: Path to the Grapevine character file
            
        Returns:
            Dictionary containing character data
        """
        data = {}
        current_section = None
        
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Check for section header
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        data[current_section] = {}
                        continue
                    
                    # Process data within a section
                    if current_section and '=' in line:
                        key, value = line.split('=', 1)
                        data[current_section][key.strip()] = value.strip()
        
        except Exception as e:
            # Handle errors
            print(f"Error loading Grapevine file: {e}")
            return {}
        
        # Process the raw data into a more usable format
        return DataLoader._process_grapevine_data(data)
    
    @staticmethod
    def load_grapevine_xml(file_path: str) -> Dict:
        """Load data from a Grapevine XML export file (.gex).
        
        Args:
            file_path: Path to the Grapevine XML file
            
        Returns:
            Dictionary containing character data
        """
        try:
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Create a dictionary to store character data
            data = {}
            
            # Process the XML data
            for element in root:
                if element.tag == 'character':
                    # Process character data
                    character = {}
                    for child in element:
                        if child.tag == 'traits':
                            # Process traits
                            traits = {}
                            for trait in child:
                                trait_type = trait.get('type')
                                if trait_type not in traits:
                                    traits[trait_type] = {}
                                
                                trait_name = trait.get('name')
                                trait_value = trait.get('value')
                                traits[trait_type][trait_name] = trait_value
                            
                            character['traits'] = traits
                        else:
                            # Process other character data
                            character[child.tag] = child.text
                    
                    # Add the character to the data dictionary
                    data['character'] = character
            
            # Process the raw XML data into a more usable format
            return DataLoader._process_grapevine_xml_data(data)
            
        except Exception as e:
            # Handle errors
            print(f"Error loading Grapevine XML file: {e}")
            return {}
    
    @staticmethod
    def _process_grapevine_data(raw_data: Dict) -> Dict:
        """Process raw Grapevine data into a standardized format.
        
        Args:
            raw_data: Raw data from a Grapevine file
            
        Returns:
            Processed character data
        """
        character = {}
        
        # Extract basic character information
        if 'Character' in raw_data:
            char_data = raw_data['Character']
            character['name'] = char_data.get('Name', '')
            character['player'] = char_data.get('Player', '')
            character['nature'] = char_data.get('Nature', '')
            character['demeanor'] = char_data.get('Demeanor', '')
            character['clan'] = char_data.get('Clan', '')
            character['generation'] = int(char_data.get('Generation', '13'))
            character['status'] = 'Active'  # Default status
            
            # Extract other character info
            for key, value in char_data.items():
                if key not in character and value:
                    character[key] = value
        
        # Extract traits
        character['traits'] = DataLoader._extract_grapevine_traits(raw_data)
        
        # Extract LARP traits (already in adjective format)
        character['larp_traits'] = DataLoader._extract_grapevine_larp_traits(raw_data)
        
        return character
    
    @staticmethod
    def _process_grapevine_xml_data(raw_data: Dict) -> Dict:
        """Process raw Grapevine XML data into a standardized format.
        
        Args:
            raw_data: Raw data from a Grapevine XML file
            
        Returns:
            Processed character data
        """
        character = {}
        
        # Extract character data from XML
        if 'character' in raw_data:
            char_data = raw_data['character']
            
            # Basic character info
            character['name'] = char_data.get('name', '')
            character['player'] = char_data.get('player', '')
            character['nature'] = char_data.get('nature', '')
            character['demeanor'] = char_data.get('demeanor', '')
            character['clan'] = char_data.get('clan', '')
            
            # Extract generation
            try:
                character['generation'] = int(char_data.get('generation', '13'))
            except ValueError:
                character['generation'] = 13
            
            character['status'] = 'Active'  # Default status
            
            # Extract other character info
            for key, value in char_data.items():
                if key not in character and key != 'traits' and value:
                    character[key] = value
            
            # Extract traits
            if 'traits' in char_data:
                character['traits'] = DataLoader._extract_xml_traits(char_data['traits'])
                
                # Also extract as LARP traits
                character['larp_traits'] = DataLoader._extract_xml_larp_traits(char_data['traits'])
        
        return character
    
    @staticmethod
    def _extract_grapevine_traits(raw_data: Dict) -> Dict:
        """Extract traits from raw Grapevine data.
        
        Args:
            raw_data: Raw Grapevine data
            
        Returns:
            Dictionary of traits categorized by type
        """
        traits = {
            'physical': {},
            'social': {},
            'mental': {},
            'talents': {},
            'skills': {},
            'knowledges': {},
            'disciplines': {},
            'backgrounds': {},
            'virtues': {},
            'merits': {},
            'flaws': {}
        }
        
        # Extract physical attributes
        if 'Physical' in raw_data:
            for key, value in raw_data['Physical'].items():
                if value and value.isdigit():
                    traits['physical'][key] = int(value)
        
        # Extract social attributes
        if 'Social' in raw_data:
            for key, value in raw_data['Social'].items():
                if value and value.isdigit():
                    traits['social'][key] = int(value)
        
        # Extract mental attributes
        if 'Mental' in raw_data:
            for key, value in raw_data['Mental'].items():
                if value and value.isdigit():
                    traits['mental'][key] = int(value)
        
        # Extract abilities
        if 'Abilities' in raw_data:
            abilities = raw_data['Abilities']
            
            # Talents
            for key in ['Alertness', 'Athletics', 'Brawl', 'Dodge', 'Empathy', 
                        'Expression', 'Intimidation', 'Leadership', 'Streetwise', 'Subterfuge']:
                if key in abilities and abilities[key] and abilities[key].isdigit():
                    traits['talents'][key] = int(abilities[key])
            
            # Skills
            for key in ['Animal Ken', 'Crafts', 'Drive', 'Etiquette', 'Firearms', 'Melee', 
                       'Performance', 'Security', 'Stealth', 'Survival']:
                if key in abilities and abilities[key] and abilities[key].isdigit():
                    traits['skills'][key] = int(abilities[key])
            
            # Knowledges
            for key in ['Academics', 'Computer', 'Finance', 'Investigation', 'Law', 'Linguistics',
                       'Medicine', 'Occult', 'Politics', 'Science']:
                if key in abilities and abilities[key] and abilities[key].isdigit():
                    traits['knowledges'][key] = int(abilities[key])
        
        # Extract backgrounds
        if 'Backgrounds' in raw_data:
            for key, value in raw_data['Backgrounds'].items():
                if value and value.isdigit():
                    traits['backgrounds'][key] = int(value)
        
        # Extract disciplines
        if 'Disciplines' in raw_data:
            for key, value in raw_data['Disciplines'].items():
                if value and value.isdigit():
                    traits['disciplines'][key] = int(value)
        
        # Extract virtues
        if 'Virtues' in raw_data:
            for key, value in raw_data['Virtues'].items():
                if value and value.isdigit():
                    traits['virtues'][key] = int(value)
        
        # Extract merits/flaws
        if 'Merits' in raw_data:
            for key, value in raw_data['Merits'].items():
                if value:
                    # Merits/flaws might have descriptions instead of values
                    traits['merits'][key] = value
        
        if 'Flaws' in raw_data:
            for key, value in raw_data['Flaws'].items():
                if value:
                    traits['flaws'][key] = value
        
        return traits
    
    @staticmethod
    def _extract_grapevine_larp_traits(raw_data: Dict) -> Dict:
        """Extract LARP traits from raw Grapevine data.
        
        Args:
            raw_data: Raw Grapevine data
            
        Returns:
            Dictionary of LARP traits as adjectives categorized by type
        """
        larp_traits = {
            'physical': [],
            'social': [],
            'mental': [],
            'talents': [],
            'skills': [],
            'knowledges': [],
            'disciplines': [],
            'backgrounds': [],
            'virtues': [],
            'merits': [],
            'flaws': []
        }
        
        # Extract dot-based traits and convert to adjectives
        traits = DataLoader._extract_grapevine_traits(raw_data)
        
        # Convert physical attributes to adjectives
        for trait_name, value in traits['physical'].items():
            adjectives = TraitConverter.dot_rating_to_adjectives(trait_name, value, 'physical')
            larp_traits['physical'].extend(adjectives)
        
        # Convert social attributes to adjectives
        for trait_name, value in traits['social'].items():
            adjectives = TraitConverter.dot_rating_to_adjectives(trait_name, value, 'social')
            larp_traits['social'].extend(adjectives)
        
        # Convert mental attributes to adjectives
        for trait_name, value in traits['mental'].items():
            adjectives = TraitConverter.dot_rating_to_adjectives(trait_name, value, 'mental')
            larp_traits['mental'].extend(adjectives)
        
        # Convert abilities to adjectives
        for category in ['talents', 'skills', 'knowledges']:
            for trait_name, value in traits[category].items():
                # Normalize trait name for lookup
                normalized_name = trait_name.lower().replace(' ', '_')
                adjectives = TraitConverter.dot_rating_to_adjectives(normalized_name, value, category)
                larp_traits[category].extend(adjectives)
        
        # Convert other traits similarly
        for category in ['disciplines', 'backgrounds', 'virtues']:
            for trait_name, value in traits[category].items():
                if isinstance(value, int):
                    # Use generic adjectives for these
                    adjectives = [f"{trait_name} {i}" for i in range(1, value + 1)]
                    larp_traits[category].extend(adjectives)
        
        # Add merits/flaws as is (they're often just descriptive)
        for trait_name in traits['merits']:
            larp_traits['merits'].append(trait_name)
        
        for trait_name in traits['flaws']:
            larp_traits['flaws'].append(trait_name)
        
        return larp_traits
    
    @staticmethod
    def _extract_xml_traits(traits_data: Dict) -> Dict:
        """Extract traits from Grapevine XML trait data.
        
        Args:
            traits_data: Trait data from Grapevine XML
            
        Returns:
            Dictionary of traits categorized by type
        """
        traits = {
            'physical': {},
            'social': {},
            'mental': {},
            'talents': {},
            'skills': {},
            'knowledges': {},
            'disciplines': {},
            'backgrounds': {},
            'virtues': {},
            'merits': {},
            'flaws': {}
        }
        
        # Map trait types to categories
        type_to_category = {
            'physical': 'physical',
            'social': 'social', 
            'mental': 'mental',
            'talent': 'talents',
            'skill': 'skills',
            'knowledge': 'knowledges',
            'discipline': 'disciplines',
            'background': 'backgrounds',
            'virtue': 'virtues',
            'merit': 'merits',
            'flaw': 'flaws'
        }
        
        # Process each trait
        for trait_type, trait_dict in traits_data.items():
            category = type_to_category.get(trait_type.lower(), 'other')
            
            if category in traits:
                for name, value in trait_dict.items():
                    try:
                        # Try to convert value to int if possible
                        int_value = int(value)
                        traits[category][name] = int_value
                    except (ValueError, TypeError):
                        # If not a number, just store as is
                        traits[category][name] = value
        
        return traits
    
    @staticmethod
    def _extract_xml_larp_traits(traits_data: Dict) -> Dict:
        """Extract LARP traits from Grapevine XML trait data.
        
        Args:
            traits_data: Trait data from Grapevine XML
            
        Returns:
            Dictionary of LARP traits as adjectives categorized by type
        """
        # First get dot-based traits
        traits = DataLoader._extract_xml_traits(traits_data)
        
        # Now convert to LARP traits the same way as with non-XML version
        larp_traits = {
            'physical': [],
            'social': [],
            'mental': [],
            'talents': [],
            'skills': [],
            'knowledges': [],
            'disciplines': [],
            'backgrounds': [],
            'virtues': [],
            'merits': [],
            'flaws': []
        }
        
        # Convert physical attributes to adjectives
        for trait_name, value in traits['physical'].items():
            if isinstance(value, int):
                adjectives = TraitConverter.dot_rating_to_adjectives(trait_name, value, 'physical')
                larp_traits['physical'].extend(adjectives)
        
        # Convert social attributes to adjectives
        for trait_name, value in traits['social'].items():
            if isinstance(value, int):
                adjectives = TraitConverter.dot_rating_to_adjectives(trait_name, value, 'social')
                larp_traits['social'].extend(adjectives)
        
        # Convert mental attributes to adjectives
        for trait_name, value in traits['mental'].items():
            if isinstance(value, int):
                adjectives = TraitConverter.dot_rating_to_adjectives(trait_name, value, 'mental')
                larp_traits['mental'].extend(adjectives)
        
        # Convert abilities to adjectives
        for category in ['talents', 'skills', 'knowledges']:
            for trait_name, value in traits[category].items():
                if isinstance(value, int):
                    # Normalize trait name for lookup
                    normalized_name = trait_name.lower().replace(' ', '_')
                    adjectives = TraitConverter.dot_rating_to_adjectives(normalized_name, value, category)
                    larp_traits[category].extend(adjectives)
        
        # Convert other traits similarly
        for category in ['disciplines', 'backgrounds', 'virtues']:
            for trait_name, value in traits[category].items():
                if isinstance(value, int):
                    # Use generic adjectives for these
                    adjectives = [f"{trait_name} {i}" for i in range(1, value + 1)]
                    larp_traits[category].extend(adjectives)
        
        # Add merits/flaws as is (they're often just descriptive)
        for trait_name in traits['merits']:
            larp_traits['merits'].append(trait_name)
        
        for trait_name in traits['flaws']:
            larp_traits['flaws'].append(trait_name)
        
        return larp_traits
    
    @staticmethod
    def create_larp_traits_from_dict(character_id: int, larp_traits_dict: Dict) -> List[LarpTrait]:
        """
        Create LarpTrait objects from a dictionary of trait lists.
        
        Args:
            character_id: The ID of the character to associate traits with
            larp_traits_dict: Dictionary mapping categories to lists of trait adjectives
            
        Returns:
            List of LarpTrait objects
        """
        # Create a dictionary to store trait categories
        trait_categories = {}
        larp_trait_objects = []
        
        # Process each trait category
        for category_name, traits in larp_traits_dict.items():
            # Get or create the category
            if category_name not in trait_categories:
                category = TraitCategory(name=category_name)
                trait_categories[category_name] = category
            else:
                category = trait_categories[category_name]
            
            # Create a trait object for each adjective
            for trait_name in traits:
                # Check if it's a negative trait
                is_negative = False
                if category_name in ['flaws'] or trait_name.startswith('Negative:'):
                    is_negative = True
                    if trait_name.startswith('Negative:'):
                        trait_name = trait_name[9:].strip()
                
                # Create the trait object
                trait = LarpTrait(
                    name=trait_name,
                    character_id=character_id,
                    is_negative=is_negative,
                    is_temporary=False,
                    is_custom=False,
                    is_spent=False
                )
                
                # Add the category to the trait
                trait.categories.append(category)
                
                # Add to the result list
                larp_trait_objects.append(trait)
        
        return larp_trait_objects
    
    @staticmethod
    def create_vampire_from_dict(character_data: Dict) -> Vampire:
        """
        Create a Vampire character from a dictionary of character data.
        
        Args:
            character_data: Dictionary containing character data from import
            
        Returns:
            Vampire object ready to be added to the database
        """
        from datetime import datetime
        
        # Get a database session
        session = get_session()
        
        try:
            # Create a new Vampire character with basic attributes
            vampire = Vampire(
                name=character_data.get('name', 'Unknown'),
                player=character_data.get('player', ''),
                nature=character_data.get('nature', ''),
                demeanor=character_data.get('demeanor', ''),
                clan=character_data.get('clan', ''),
                generation=character_data.get('generation', 13),
                sect=character_data.get('sect', ''),
                status=character_data.get('status', 'Active'),
                start_date=datetime.now(),
                last_modified=datetime.now(),
                
                # Virtues
                conscience=character_data.get('conscience', 0),
                temp_conscience=character_data.get('temp_conscience', 0),
                self_control=character_data.get('self_control', 0),
                temp_self_control=character_data.get('temp_self_control', 0),
                courage=character_data.get('courage', 0),
                temp_courage=character_data.get('temp_courage', 0),
                
                # Path
                path=character_data.get('path', 'Humanity'),
                path_traits=character_data.get('path_traits', 0),
                temp_path_traits=character_data.get('temp_path_traits', 0),
                
                # Stats
                willpower=character_data.get('willpower', 0),
                temp_willpower=character_data.get('temp_willpower', 0),
                blood=character_data.get('blood', 0),
                temp_blood=character_data.get('temp_blood', 0)
            )
            
            # Add to session to get an ID
            session.add(vampire)
            session.commit()  # Commit to DB to ensure all relationships are saved
            
            # Add LARP traits if present
            if 'larp_traits' in character_data and character_data['larp_traits']:
                larp_traits = DataLoader.create_larp_traits_from_dict(
                    vampire.id, character_data['larp_traits']
                )
                for trait in larp_traits:
                    session.add(trait)
            
            # Add legacy traits if present and no LARP traits were provided
            elif 'traits' in character_data and character_data['traits']:
                for trait_data in character_data['traits']:
                    trait = Trait(
                        character_id=vampire.id,
                        name=trait_data['name'],
                        value=trait_data['value'],
                        note=trait_data.get('note', ''),
                        category=trait_data['category'],
                        type=trait_data['type']
                    )
                    if 'temp_value' in trait_data:
                        trait.temp_value = trait_data['temp_value']
                    session.add(trait)
            
            # Commit changes to DB
            session.commit()
            
            return vampire
            
        except Exception as e:
            session.rollback()
            raise ValueError(f"Failed to create vampire from data: {str(e)}")
    
    @staticmethod
    def load_json_file(file_path: str) -> Dict:
        """Load data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary containing the JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return {}

    @staticmethod
    def load_character(character_id: int) -> Optional[Any]:
        """
        Safely load a character from the database with proper session handling.
        
        Args:
            character_id: ID of the character to load
            
        Returns:
            Character object or None if not found
        """
        from coterie.models.base import Character
        
        session = get_session()
        try:
            # Fetch the character from the database
            character = session.query(Character).filter(Character.id == character_id).first()
            
            # If found, prepare it for UI use
            if character:
                # First, while the character is attached to this session, refresh it
                session.refresh(character)
                
                # Close this session before returning
                session.expunge(character)
                session.close()
                
                # Now prepare the character in a new session to preload all attributes
                return DataLoader.prepare_character_for_ui(character)
            
            return None
            
        except Exception as e:
            print(f"Error loading character {character_id}: {e}")
            return None
        finally:
            # Only close if it hasn't been closed already
            if session and session.is_active:
                session.close()

    @staticmethod
    def prepare_character_for_ui(character: Any) -> Any:
        """
        Prepare a character for use in the UI by ensuring all required data is loaded.
        This helps prevent lazy loading issues when the object is detached from the session.
        
        Args:
            character: Character object to prepare
            
        Returns:
            Prepared character object
        """
        if not character:
            return None
            
        # Create a new session and attach the character to it
        session = get_session()
        try:
            # Add the character to the session
            session.add(character)
            
            # Force access to key attributes to ensure they're loaded
            _ = character.id
            _ = character.name
            _ = character.player
            _ = character.nature
            _ = character.demeanor
            _ = character.type
            
            # Access type-specific attributes
            from coterie.models.vampire import Vampire
            if isinstance(character, Vampire):
                _ = character.clan
                _ = character.generation
                _ = character.sect
                _ = character.conscience
                _ = character.self_control
                _ = character.courage
                _ = character.path
                _ = character.willpower
                _ = character.blood
                
            # Force load all collection attributes
            if hasattr(character, 'traits'):
                traits = list(character.traits)  # Force loading full collection
                
            if hasattr(character, 'larp_traits'):
                larp_traits = list(character.larp_traits)  # Force loading full collection
                # Also load each larp_trait's categories
                for trait in larp_traits:
                    if hasattr(trait, 'categories'):
                        _ = list(trait.categories)  # Force loading categories
                
            return character
            
        except Exception as e:
            print(f"Error preparing character for UI: {e}")
            return character
        finally:
            session.close() 