"""Utility for loading game data from JSON files."""

import json
import os
from typing import Dict, List, Any, Optional, Union
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