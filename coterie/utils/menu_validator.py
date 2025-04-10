import logging
from pathlib import Path
from typing import List, Tuple, Dict
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

logger = logging.getLogger(__name__)

class MenuValidator:
    """Validator for Grapevine menu files."""
    
    @staticmethod
    def validate_menu_file(file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate a Grapevine menu file.
        
        Args:
            file_path: Path to the menu file to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check root element
            if root.tag != "menus":
                errors.append("Root element must be <menus>")
            
            # Check each menu element
            for menu_idx, menu in enumerate(root.findall("menu"), 1):
                # Required attributes
                name = menu.get("name")
                if not name:
                    errors.append(f"Menu #{menu_idx} missing required 'name' attribute")
                
                # Optional attributes with type validation
                display = menu.get("display")
                if display is not None:
                    try:
                        int(display)
                    except ValueError:
                        errors.append(f"Menu '{name}': 'display' must be an integer")
                
                # Boolean attributes
                abc = menu.get("abc", "").lower()
                if abc and abc not in ("yes", "no"):
                    errors.append(f"Menu '{name}': 'abc' must be 'yes' or 'no'")
                
                required = menu.get("required", "").lower()
                if required and required not in ("yes", "no"):
                    errors.append(f"Menu '{name}': 'required' must be 'yes' or 'no'")
                
                # Check items
                for item_idx, item in enumerate(menu.findall("item"), 1):
                    name = item.get("name")
                    if not name:
                        errors.append(f"Menu '{menu.get('name')}' item #{item_idx} missing required 'name' attribute")
                    
                    # Cost validation if present
                    cost = item.get("cost")
                    if cost:
                        try:
                            # Handle ranges like "1-5"
                            if "-" in cost:
                                low, high = map(int, cost.split("-"))
                                if low > high:
                                    errors.append(f"Item '{name}': invalid cost range {cost}")
                            else:
                                int(cost)
                        except ValueError:
                            errors.append(f"Item '{name}': invalid cost value '{cost}'")
                
                # Check submenus
                for submenu_idx, submenu in enumerate(menu.findall("submenu"), 1):
                    name = submenu.get("name")
                    if not name:
                        errors.append(f"Menu '{menu.get('name')}' submenu #{submenu_idx} missing required 'name' attribute")
                    
                    # Check link attribute if present
                    link = submenu.get("link")
                    if link and not any(m.get("name") == link for m in root.findall("menu")):
                        errors.append(f"Submenu '{name}': linked menu '{link}' not found")
            
            return not errors, errors
            
        except ParseError as e:
            errors.append(f"XML parsing error: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"Validation error: {e}")
            return False, errors
    
    @staticmethod
    def validate_directory(directory: str, pattern: str = "*.gvm") -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate all menu files in a directory.
        
        Args:
            directory: Directory containing menu files
            pattern: Glob pattern for menu files
            
        Returns:
            Dictionary mapping file paths to (is_valid, errors) tuples
        """
        results = {}
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.error(f"Directory not found: {directory}")
            return results
            
        for file_path in dir_path.glob(pattern):
            results[str(file_path)] = MenuValidator.validate_menu_file(str(file_path))
            
        return results 