"""Utility module for converting between trait systems.

This module provides utility functions for converting between the dot-based
trait system used in tabletop Vampire: The Masquerade and the adjective-based
trait system used in Mind's Eye Theater LARP.
"""

from typing import List, Dict, Tuple, Set
import json
import os
from pathlib import Path

class TraitConverter:
    """Utility class for converting between trait systems."""
    
    # Default trait adjectives by rating (from LARP rulebook)
    DEFAULT_TRAIT_ADJECTIVES = {
        "physical": {
            1: ["Brawny", "Enduring", "Rugged", "Steady", "Tough"],
            2: ["Brutish", "Energetic", "Stalwart", "Strapping", "Tenacious"],
            3: ["Athletic", "Agile", "Dexterous", "Resilient", "Vigorous"],
            4: ["Lithe", "Nimble", "Robust", "Swift", "Tireless"],
            5: ["Commanding", "Powerful", "Quick", "Relentless", "Mighty"]
        },
        "social": {
            1: ["Charming", "Eloquent", "Expressive", "Persuasive", "Sensual"],
            2: ["Alluring", "Graceful", "Magnetic", "Suave", "Tactful"],
            3: ["Beguiling", "Charismatic", "Dignified", "Elegant", "Seductive"],
            4: ["Captivating", "Dazzling", "Entrancing", "Fascinating", "Mesmerizing"],
            5: ["Bewitching", "Compelling", "Enchanting", "Irresistible", "Magnificent"]
        },
        "mental": {
            1: ["Attentive", "Clever", "Discerning", "Insightful", "Knowledgeable"],
            2: ["Analytical", "Astute", "Cunning", "Focused", "Intuitive"],
            3: ["Brilliant", "Erudite", "Perceptive", "Rational", "Shrewd"],
            4: ["Calculating", "Enlightened", "Ingenious", "Learned", "Visionary"],
            5: ["Creative", "Inspired", "Mastermind", "Sagacious", "Wise"]
        }
    }
    
    # Standard adjectives for abilities
    ABILITY_ADJECTIVES = {
        # Talents
        "alertness": ["Alert", "Vigilant", "Watchful", "Observant", "Perceptive"],
        "athletics": ["Athletic", "Agile", "Nimble", "Coordinated", "Limber"],
        "brawl": ["Scrappy", "Combative", "Tough", "Pugnacious", "Fierce"],
        "dodge": ["Evasive", "Quick", "Elusive", "Agile", "Dexterous"],
        "empathy": ["Empathic", "Sensitive", "Sympathetic", "Compassionate", "Understanding"],
        "expression": ["Articulate", "Expressive", "Persuasive", "Eloquent", "Poetic"],
        "intimidation": ["Intimidating", "Imposing", "Frightening", "Menacing", "Terrifying"],
        "leadership": ["Commanding", "Inspiring", "Authoritative", "Decisive", "Influential"],
        "streetwise": ["Streetwise", "Savvy", "Worldly", "Connected", "Shrewd"],
        "subterfuge": ["Deceptive", "Cunning", "Sly", "Manipulative", "Devious"],
        
        # Skills
        "animal_ken": ["Animal-friendly", "Soothing", "Nurturing", "Familiar", "Connected"],
        "crafts": ["Crafty", "Handy", "Skilled", "Meticulous", "Creative"],
        "drive": ["Driver", "Operator", "Pilot", "Steady", "Quick"],
        "etiquette": ["Proper", "Polite", "Refined", "Cultured", "Diplomatic"],
        "firearms": ["Armed", "Accurate", "Precise", "Trained", "Marksman"],
        "melee": ["Armed", "Trained", "Skilled", "Proficient", "Adept"],
        "performance": ["Performer", "Entertaining", "Captivating", "Dramatic", "Showman"],
        "security": ["Cautious", "Secure", "Locksmith", "Vigilant", "Protective"],
        "stealth": ["Stealthy", "Silent", "Hidden", "Covert", "Sneaky"],
        "survival": ["Survivalist", "Hardy", "Adaptable", "Resourceful", "Prepared"],
        
        # Knowledges
        "academics": ["Academic", "Educated", "Scholarly", "Studious", "Knowledgeable"],
        "computer": ["Technical", "Programmer", "Hacker", "Digital", "Analytical"],
        "finance": ["Financial", "Economic", "Fiscal", "Resourceful", "Calculating"],
        "investigation": ["Investigative", "Thorough", "Meticulous", "Analytical", "Deductive"],
        "law": ["Legal", "Judicial", "Legislative", "Authoritative", "Constitutional"],
        "linguistics": ["Linguistic", "Multilingual", "Fluent", "Articulate", "Expressive"],
        "medicine": ["Medical", "Therapeutic", "Diagnostic", "Healing", "Scientific"],
        "occult": ["Occult", "Mystical", "Arcane", "Esoteric", "Knowledgeable"],
        "politics": ["Political", "Diplomatic", "Strategic", "Connected", "Influential"],
        "science": ["Scientific", "Analytical", "Technical", "Experimental", "Methodical"]
    }
    
    # Path to the data directory
    DATA_DIR = Path(__file__).parent.parent / "data"
    
    @classmethod
    def load_trait_adjective_mappings(cls) -> Dict:
        """
        Load trait adjective mappings from the data files.
        
        Returns:
            Dictionary mapping trait categories and values to adjectives
        """
        trait_file = cls.DATA_DIR / "trait_adjectives.json"
        
        # If the file doesn't exist, use default mappings
        if not trait_file.exists():
            return cls.DEFAULT_TRAIT_ADJECTIVES
            
        with open(trait_file, "r") as f:
            return json.load(f)
    
    @classmethod
    def dot_rating_to_adjectives(cls, trait_name: str, rating: int, category: str) -> List[str]:
        """
        Convert a dot rating to a list of adjective traits.
        
        Args:
            trait_name: The name of the trait
            rating: The dot rating (1-5)
            category: The trait category (physical, social, mental, etc.)
            
        Returns:
            List of adjective traits corresponding to the rating
        """
        # Normalize inputs
        trait_name = trait_name.lower()
        category = category.lower()
        
        # Ensure rating is in valid range
        rating = max(0, min(5, rating))
        
        # Return empty list for zero rating
        if rating == 0:
            return []
            
        # Check if this is an ability with defined adjectives
        if trait_name in cls.ABILITY_ADJECTIVES:
            # Return the number of adjectives based on rating
            return cls.ABILITY_ADJECTIVES[trait_name][:rating]
            
        # Otherwise, use the general mappings based on category
        adjective_mappings = cls.load_trait_adjective_mappings()
        
        # If category exists in mappings
        if category in adjective_mappings and rating in adjective_mappings[category]:
            # Return a subset of adjectives based on rating
            available_adjectives = adjective_mappings[category][str(rating)]
            return available_adjectives[:rating]
            
        # Fallback to default descriptive adjectives
        return [f"Level {rating}"] * rating
    
    @classmethod
    def adjectives_to_dot_rating(cls, adjectives: List[str], category: str) -> int:
        """
        Convert a list of adjective traits to an approximate dot rating.
        
        Args:
            adjectives: List of adjective traits
            category: The trait category
            
        Returns:
            Approximate dot rating (0-5)
        """
        # Simple mapping based on number of traits
        num_traits = len(adjectives)
        
        # Cap at 5 dots maximum
        return min(num_traits, 5)
    
    @classmethod
    def get_all_category_adjectives(cls, category: str) -> Dict[int, List[str]]:
        """
        Get all available adjectives for a category by rating.
        
        Args:
            category: The trait category (physical, social, mental)
            
        Returns:
            Dictionary mapping ratings to lists of adjectives
        """
        adjective_mappings = cls.load_trait_adjective_mappings()
        
        if category.lower() in adjective_mappings:
            return adjective_mappings[category.lower()]
        
        # Return empty dict if category not found
        return {}
    
    @classmethod
    def get_all_ability_adjectives(cls, ability_name: str) -> List[str]:
        """
        Get all available adjectives for an ability.
        
        Args:
            ability_name: The name of the ability
            
        Returns:
            List of adjectives for the ability
        """
        ability_name = ability_name.lower()
        
        if ability_name in cls.ABILITY_ADJECTIVES:
            return cls.ABILITY_ADJECTIVES[ability_name]
        
        # Return empty list if ability not found
        return [] 