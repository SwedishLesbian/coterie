"""Parser for Grapevine menu files."""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session

from ..models.menu import Menu, MenuCategory, MenuItem

class MenuParser:
    """Parser for Grapevine XML menu files."""
    
    @staticmethod
    def parse_menu_file(file_path: str, session: Session) -> Tuple[List[MenuCategory], List[MenuItem]]:
        """
        Parse a Grapevine menu file and create corresponding database entries.
        
        Args:
            file_path: Path to the XML menu file
            session: SQLAlchemy session
            
        Returns:
            Tuple of (categories, items) created from the menu file
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        categories: Dict[str, MenuCategory] = {}
        items: List[MenuItem] = []
        
        # First pass: Create categories
        for menu_elem in root.findall("menu"):
            name = menu_elem.get("name", "")
            if not name:
                continue
                
            category = MenuCategory(
                name=name,
                display_order=int(menu_elem.get("display", "0")),
                alphabetical=menu_elem.get("abc", "no").lower() == "yes",
                required=menu_elem.get("required", "no").lower() == "yes"
            )
            categories[name] = category
            session.add(category)
        
        # Second pass: Create items and handle submenus
        for menu_elem in root.findall("menu"):
            category_name = menu_elem.get("name", "")
            if not category_name or category_name not in categories:
                continue
                
            category = categories[category_name]
            
            # Process items
            for item_elem in menu_elem.findall("item"):
                name = item_elem.get("name", "")
                if not name:
                    continue
                    
                cost_str = item_elem.get("cost", "")
                cost = None
                if cost_str:
                    try:
                        cost = int(cost_str)
                    except ValueError:
                        # Handle ranges like "1-5" by taking the lower value
                        if "-" in cost_str:
                            cost = int(cost_str.split("-")[0])
                
                item = MenuItem(
                    name=name,
                    cost=cost,
                    note=item_elem.get("note"),
                    category=category
                )
                items.append(item)
                session.add(item)
            
            # Process submenus
            for submenu_elem in menu_elem.findall("submenu"):
                name = submenu_elem.get("name", "")
                link = submenu_elem.get("link", name)
                if not name:
                    continue
                
                # Create a placeholder item for the submenu
                submenu_item = MenuItem(
                    name=name,
                    category=category
                )
                items.append(submenu_item)
                session.add(submenu_item)
                
                # Store the link information for later resolution
                if link != name:
                    # TODO: Store link information to resolve after all menus are loaded
                    pass
        
        session.flush()
        return list(categories.values()), items
    
    @staticmethod
    def fuzzy_match_trait(trait_name: str, existing_traits: List[MenuItem], threshold: float = 0.8) -> Optional[MenuItem]:
        """
        Find an existing trait that closely matches the given name using fuzzy matching.
        
        Args:
            trait_name: Name of the trait to match
            existing_traits: List of existing menu items to match against
            threshold: Minimum similarity score (0-1) required for a match
            
        Returns:
            The best matching MenuItem or None if no match meets the threshold
        """
        from difflib import SequenceMatcher
        
        best_match = None
        best_score = 0.0
        
        for trait in existing_traits:
            score = SequenceMatcher(None, trait_name.lower(), trait.name.lower()).ratio()
            if score > best_score and score >= threshold:
                best_match = trait
                best_score = score
        
        return best_match 