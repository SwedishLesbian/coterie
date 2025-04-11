"""Menu importer for handling Grapevine menu files."""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from PyQt6.QtWidgets import QApplication

from .menu_parser import MenuParser
from ..models.menu import Menu, MenuCategory, MenuItem
from ..ui.dialogs.trait_conflict import TraitConflictDialog

logger = logging.getLogger(__name__)

class MenuImporter:
    """Utility class for importing Grapevine menu files."""
    
    def __init__(self, session: Session, parent_widget=None):
        """
        Initialize the menu importer.
        
        Args:
            session: SQLAlchemy session for database operations
            parent_widget: Parent widget for dialogs
        """
        self.session = session
        self.parser = MenuParser()
        self.parent = parent_widget
        
    def import_menu_file(self, file_path: str, interactive: bool = True) -> bool:
        """
        Import a single menu file.
        
        Args:
            file_path: Path to the .gvm file to import
            interactive: Whether to show conflict resolution dialogs
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            logger.info(f"Importing menu file: {file_path}")
            categories, items = MenuParser.parse_menu_file(file_path, self.session)
            
            # Handle conflicts if in interactive mode
            if interactive:
                for item in items:
                    similar = self.find_similar_trait(item.name, item.category.name if item.category else None)
                    if similar:
                        resolved = TraitConflictDialog.resolve_conflict(item, similar, self.parent)
                        if resolved == similar:
                            # Remove the new item if keeping existing
                            self.session.delete(item)
                        elif resolved is None:
                            # Keep both, no action needed
                            pass
                        else:
                            # Use new item, remove existing
                            self.session.delete(similar)
            
            logger.info(f"Successfully imported {len(categories)} categories and {len(items)} items")
            self.session.commit()
            return True
            
        except ParseError as e:
            logger.error(f"Failed to parse menu file {file_path}: {e}")
            self.session.rollback()
            return False
            
        except Exception as e:
            logger.error(f"Error importing menu file {file_path}: {e}")
            self.session.rollback()
            return False
    
    def import_directory(self, directory: str, pattern: str = "*.gvm", interactive: bool = True) -> Dict[str, bool]:
        """
        Import all menu files in a directory.
        
        Args:
            directory: Directory containing menu files
            pattern: Glob pattern for menu files (default: "*.gvm")
            interactive: Whether to show conflict resolution dialogs
            
        Returns:
            Dictionary mapping file paths to import success status
        """
        results = {}
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.error(f"Directory not found: {directory}")
            return results
            
        for file_path in dir_path.glob(pattern):
            results[str(file_path)] = self.import_menu_file(str(file_path), interactive)
            
        return results
    
    def import_specific_menus(self, menu_names: List[str], directory: str) -> Dict[str, bool]:
        """
        Import specific menu files by name.
        
        Args:
            menu_names: List of menu names to import (without .gvm extension)
            directory: Directory containing menu files
            
        Returns:
            Dictionary mapping menu names to import success status
        """
        results = {}
        dir_path = Path(directory)
        
        for name in menu_names:
            # Try both with and without .gvm extension
            paths = [
                dir_path / f"{name}.gvm",
                dir_path / name
            ]
            
            imported = False
            for path in paths:
                if path.exists():
                    results[name] = self.import_menu_file(str(path))
                    imported = True
                    break
                    
            if not imported:
                logger.error(f"Menu file not found: {name}")
                results[name] = False
                
        return results
    
    def get_existing_traits(self, category_name: Optional[str] = None) -> List[MenuItem]:
        """
        Get existing menu items, optionally filtered by category.
        
        Args:
            category_name: Optional category name to filter by
            
        Returns:
            List of existing menu items
        """
        query = self.session.query(MenuItem)
        if category_name:
            query = query.join(MenuCategory).filter(MenuCategory.name == category_name)
        return query.all()
    
    def find_similar_trait(self, trait_name: str, category_name: Optional[str] = None) -> Optional[MenuItem]:
        """
        Find an existing trait that closely matches the given name.
        
        Args:
            trait_name: Name of the trait to match
            category_name: Optional category to search within
            
        Returns:
            The best matching MenuItem or None if no match found
        """
        existing_traits = self.get_existing_traits(category_name)
        return MenuParser.fuzzy_match_trait(trait_name, existing_traits)
    
    def resolve_trait_conflict(self, new_trait: MenuItem, existing_trait: MenuItem) -> MenuItem:
        """
        Resolve a conflict between a new trait and an existing similar trait.
        
        This method should be called when a fuzzy match is found during import.
        It will merge properties from the new trait into the existing one if they
        don't conflict, or create a new trait if they do.
        
        Args:
            new_trait: The new trait being imported
            existing_trait: The existing similar trait
            
        Returns:
            The resolved MenuItem (either existing_trait or new_trait)
        """
        # If they're exactly the same, use existing
        if new_trait.name.lower() == existing_trait.name.lower():
            return existing_trait
            
        # If they have different costs or notes, keep both
        if new_trait.cost != existing_trait.cost or new_trait.note != existing_trait.note:
            return new_trait
            
        # If they're in different categories, add new trait to existing categories
        if new_trait.category and new_trait.category not in existing_trait.category.parent_menus:
            existing_trait.category.parent_menus.append(new_trait.category)
            return existing_trait
            
        # Default to keeping both to avoid data loss
        return new_trait 