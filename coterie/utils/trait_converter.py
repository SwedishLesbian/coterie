"""Utility module for trait system management.

This module provides utility functions for managing traits in the
Mind's Eye Theater LARP system and for converting between different data formats.
"""

from typing import List, Dict, Set
import json
import os
from pathlib import Path

class TraitConverter:
    """Utility class for trait system management in Mind's Eye Theater LARP."""
    
    # Path to the data directory
    DATA_DIR = Path(__file__).parent.parent / "data"
    
    @classmethod
    def load_trait_adjectives(cls) -> Dict:
        """
        Load trait adjectives from the data files.
        
        Returns:
            Dictionary of trait adjectives by category
        """
        trait_file = cls.DATA_DIR / "trait_adjectives.json"
        
        # If the file doesn't exist, use an empty dictionary
        if not trait_file.exists():
            return {}
            
        with open(trait_file, "r") as f:
            return json.load(f)
    
    @classmethod
    def get_trait_adjectives(cls, category: str) -> List[str]:
        """
        Get all available trait adjectives for a category.
        
        Args:
            category: The trait category (physical, social, mental, etc.)
            
        Returns:
            List of trait adjectives for the category
        """
        adjectives = cls.load_trait_adjectives()
        category = category.lower()
        
        if category in adjectives:
            return adjectives[category]
        
        # Return empty list if category not found
        return []
    
    @classmethod
    def get_negative_trait_adjectives(cls, category: str) -> List[str]:
        """
        Get all available negative trait adjectives for a category.
        
        Args:
            category: The trait category (physical, social, mental)
            
        Returns:
            List of negative trait adjectives for the category
        """
        adjectives = cls.load_trait_adjectives()
        category = category.lower()
        
        if "negative" in adjectives and category in adjectives["negative"]:
            return adjectives["negative"][category]
        
        # Return empty list if category not found
        return []
    
    @classmethod
    def get_ability_trait_adjectives(cls, ability_type: str, ability_name: str) -> List[str]:
        """
        Get trait adjectives for a specific ability.
        
        Args:
            ability_type: The type of ability (talents, skills, knowledges)
            ability_name: The specific ability name
            
        Returns:
            List of trait adjectives for the ability
        """
        adjectives = cls.load_trait_adjectives()
        ability_type = ability_type.lower()
        ability_name = ability_name.lower()
        
        if ability_type in adjectives and ability_name in adjectives[ability_type]:
            return adjectives[ability_type][ability_name]
        
        # Return empty list if ability not found
        return []
    
    @classmethod
    def get_random_trait_adjectives(cls, category: str, count: int = 3) -> List[str]:
        """
        Get a random selection of trait adjectives for a category.
        
        Args:
            category: The trait category
            count: Number of adjectives to return
            
        Returns:
            List of randomly selected trait adjectives
        """
        import random
        
        adjectives = cls.get_trait_adjectives(category)
        
        if not adjectives:
            return []
            
        # Return a random selection of traits, up to the requested count
        return random.sample(adjectives, min(count, len(adjectives)))
    
    @classmethod
    def format_trait_for_display(cls, trait: str, is_negative: bool = False, 
                                is_spent: bool = False) -> str:
        """
        Format a trait for display.
        
        Args:
            trait: The trait adjective
            is_negative: Whether this is a negative trait
            is_spent: Whether this trait has been spent
            
        Returns:
            Formatted trait string
        """
        display = trait
        
        if is_negative:
            display = f"Negative: {display}"
            
        if is_spent:
            display = f"{display} (Spent)"
            
        return display 