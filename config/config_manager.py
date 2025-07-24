"""
Configuration manager for Revolution Idle Sacrifice Automation Script.

This module handles loading and saving of configuration data including
click coordinates and target RGB colors for zodiac slots and sacrifice button.
Supports both simple and advanced configuration modes.
"""

import json
import logging
from typing import Dict, Any

from config.settings import CONFIG_FILE

# Set up logging
logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration data for the automation script."""

    def __init__(self) -> None:
        # Simple mode configuration (backward compatibility)
        self.click_coords: Dict = {}
        self.target_rgbs: Dict = {}

        # Full configuration structure
        self.config_data: Dict[str, Any] = {
            "simple_mode": {"click_coords": {}, "target_rgbs": {}},
            "advanced_mode": {},
            "active_mode": "simple",
        }

        # Load existing configuration if available
        self.load_config()

    def save_config(self, mode: str = "simple") -> bool:
        """
        Saves the current configuration to a JSON file.

        Args:
            mode: Configuration mode ("simple" or "advanced")

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Update the active mode
            self.config_data["active_mode"] = mode

            # Update the appropriate mode configuration
            if mode == "simple":
                self.config_data["simple_mode"] = {
                    "click_coords": self.click_coords,
                    "target_rgbs": self.target_rgbs,
                }
            elif mode == "advanced":
                # Advanced mode configuration is set via save_advanced_config
                pass

            # Save the full configuration structure
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4)

            logger.info("Configuration saved successfully in %s mode", mode)
            return True

        except json.JSONDecodeError as e:
            logger.error("JSON encoding error: %s", e)
            print(f"ERROR: Could not encode configuration as JSON: {e}")
            return False
        except PermissionError as e:
            logger.error("Permission error: %s", e)
            print(f"ERROR: Permission denied when saving configuration: {e}")
            return False
        except IOError as e:
            logger.error("IO error saving configuration: %s", e)
            print(f"ERROR: Could not save configuration file: {e}")
            return False

    def save_advanced_config(self, advanced_config: Dict[str, Any]) -> bool:
        """
        Saves advanced configuration data.

        Args:
            advanced_config: Advanced configuration data

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Update the advanced mode configuration
            self.config_data["advanced_mode"] = advanced_config
            self.config_data["active_mode"] = "advanced"

            # Update simple mode fields for backward compatibility
            if "click_coords" in advanced_config:
                self.click_coords = advanced_config["click_coords"]
            if "target_rgbs" in advanced_config:
                self.target_rgbs = advanced_config["target_rgbs"]

            # Save to file
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4)

            logger.info("Advanced configuration saved successfully")
            return True

        except json.JSONDecodeError as e:
            logger.error("JSON encoding error: %s", e)
            print(f"ERROR: Could not encode advanced configuration as JSON: {e}")
            return False
        except PermissionError as e:
            logger.error("Permission error: %s", e)
            print(f"ERROR: Permission denied when saving advanced configuration: {e}")
            return False
        except IOError as e:
            logger.error("IO error saving advanced configuration: %s", e)
            print(f"ERROR: Could not save advanced configuration file: {e}")
            return False

    def load_config(self) -> bool:
        """
        Loads configuration from a JSON file.
        Supports both legacy format and new simple/advanced format.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)

                # Check if this is the new format with mode separation
                if "simple_mode" in config or "advanced_mode" in config:
                    # New format
                    self.config_data = config

                    # Set defaults if missing
                    if "simple_mode" not in self.config_data:
                        self.config_data["simple_mode"] = {
                            "click_coords": {},
                            "target_rgbs": {},
                        }
                    if "advanced_mode" not in self.config_data:
                        self.config_data["advanced_mode"] = {}
                    if "active_mode" not in self.config_data:
                        self.config_data["active_mode"] = "simple"

                    # Load active configuration into legacy fields for backward compatibility
                    active_mode = self.config_data.get("active_mode", "simple")
                    if active_mode == "advanced" and self.config_data["advanced_mode"]:
                        # Load from advanced mode
                        advanced_config = self.config_data["advanced_mode"]
                        self.click_coords = self._convert_coords_from_json(
                            advanced_config.get("click_coords", {})
                        )
                        self.target_rgbs = self._convert_rgbs_from_json(
                            advanced_config.get("target_rgbs", {})
                        )
                    else:
                        # Load from simple mode
                        simple_config = self.config_data["simple_mode"]
                        self.click_coords = simple_config.get("click_coords", {})
                        self.target_rgbs = self._convert_rgbs_from_json(
                            simple_config.get("target_rgbs", {})
                        )

                else:
                    # Legacy format - migrate to new structure
                    logger.info("Migrating legacy configuration format")
                    self.click_coords = config.get("click_coords", {})
                    self.target_rgbs = self._convert_rgbs_from_json(
                        config.get("target_rgbs", {})
                    )

                    # Create new structure
                    self.config_data = {
                        "simple_mode": {
                            "click_coords": self.click_coords,
                            "target_rgbs": config.get(
                                "target_rgbs", {}
                            ),  # Keep raw format for saving
                        },
                        "advanced_mode": {},
                        "active_mode": "simple",
                    }

                    # Save the migrated format
                    self.save_config("simple")

            return True

        except FileNotFoundError:
            logger.info("Configuration file '%s' not found", CONFIG_FILE)
            print(
                f"Configuration file '{CONFIG_FILE}' not found. Please run in 'setup' mode first."
            )
            return False
        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", e)
            print(
                f"ERROR: Error decoding JSON from '{CONFIG_FILE}'. File might be corrupted."
            )
            return False
        except PermissionError as e:
            logger.error("Permission error: %s", e)
            print(f"ERROR: Permission denied when reading configuration: {e}")
            return False
        except IOError as e:
            logger.error("IO error loading configuration: %s", e)
            print(f"ERROR: Could not read configuration file: {e}")
            return False

    def _convert_rgbs_from_json(self, loaded_target_rgbs: Dict) -> Dict:
        """Convert RGB data from JSON format to tuples."""
        target_rgbs: Dict[str, Any] = {}

        # Handle zodiac_slots as a list of RGB tuples
        if "zodiac_slots" in loaded_target_rgbs:
            target_rgbs["zodiac_slots"] = [
                tuple(rgb) for rgb in loaded_target_rgbs["zodiac_slots"]
            ]

        # Handle sacrifice_button - always use hardcoded RGB value
        # The sacrifice button RGB is always (217, 123, 0) regardless of mode
        target_rgbs["sacrifice_button"] = (217, 123, 0)

        return target_rgbs

    def _convert_coords_from_json(self, loaded_coords: Dict) -> Dict:
        """Convert coordinate data from JSON format to tuples for automation engine compatibility."""
        coords: Dict[str, Any] = {}

        for key, value in loaded_coords.items():
            if key == "zodiac_slots":
                # Convert list of lists [[x, y], [x, y]] to list of tuples [(x, y), (x, y)]
                if isinstance(value, list):
                    coords[key] = [
                        tuple(coord) if isinstance(coord, list) else coord
                        for coord in value
                    ]
                else:
                    coords[key] = value
            elif key in ["sacrifice_box", "sacrifice_button"]:
                # Convert [[x, y]] to [x, y] for single coordinates
                if isinstance(value, list) and len(value) > 0:
                    if isinstance(value[0], list):
                        coords[key] = value[0]  # Take first element [[x, y]] -> [x, y]
                    else:
                        coords[key] = value  # Already in correct format [x, y]
                else:
                    coords[key] = value
            else:
                coords[key] = value

        return coords

    def validate_config(self) -> bool:
        """
        Validates that all necessary configuration data is present.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        required_keys = ["zodiac_slots", "sacrifice_box", "sacrifice_button"]
        coords_valid = all(k in self.click_coords for k in required_keys)
        rgbs_valid = all(
            k in self.target_rgbs for k in ["zodiac_slots", "sacrifice_button"]
        )

        if not coords_valid or not rgbs_valid:
            return False

        # Verify we have at least one zodiac slot configured
        if (
            not self.click_coords["zodiac_slots"]
            or not self.target_rgbs["zodiac_slots"]
        ):
            return False

        return True

    def get_zodiac_count(self) -> int:
        """Returns the number of configured zodiac slots."""
        return len(self.click_coords.get("zodiac_slots", []))

    def get_active_mode(self) -> str:
        """Get the currently active configuration mode."""
        return self.config_data.get("active_mode", "simple")

    def has_simple_config(self) -> bool:
        """Check if simple mode configuration exists."""
        simple_config = self.config_data.get("simple_mode", {})
        return bool(simple_config.get("click_coords")) and bool(
            simple_config.get("target_rgbs")
        )

    def has_advanced_config(self) -> bool:
        """Check if advanced mode configuration exists."""
        advanced_config = self.config_data.get("advanced_mode", {})
        return bool(advanced_config) and advanced_config.get("advanced_mode", False)

    def get_advanced_config(self) -> Dict[str, Any]:
        """Get the advanced configuration data."""
        return self.config_data.get("advanced_mode", {})

    def get_simple_config(self) -> Dict[str, Any]:
        """Get the simple configuration data."""
        return self.config_data.get("simple_mode", {})
