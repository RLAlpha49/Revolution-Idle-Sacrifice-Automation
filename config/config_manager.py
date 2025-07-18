"""
Configuration manager for Revolution Idle Sacrifice Automation Script.

This module handles loading and saving of configuration data including
click coordinates and target RGB colors for zodiac slots and sacrifice button.
"""

import json
import logging
from typing import Dict

from config.settings import CONFIG_FILE

# Set up logging
logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration data for the automation script."""

    def __init__(self) -> None:
        self.click_coords: Dict = {}
        self.target_rgbs: Dict = {}

    def save_config(self) -> bool:
        """
        Saves the current click_coords and target_rgbs to a JSON file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "click_coords": self.click_coords,
                        "target_rgbs": self.target_rgbs,
                    },
                    f,
                    indent=4,
                )
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

    def load_config(self) -> bool:
        """
        Loads click_coords and target_rgbs from a JSON file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.click_coords = config.get("click_coords", {})

                # Convert RGB data back to proper format
                loaded_target_rgbs = config.get("target_rgbs", {})
                self.target_rgbs = {}

                # Handle zodiac_slots as a list of RGB tuples
                if "zodiac_slots" in loaded_target_rgbs:
                    self.target_rgbs["zodiac_slots"] = [
                        tuple(rgb) for rgb in loaded_target_rgbs["zodiac_slots"]
                    ]

                # Handle sacrifice_button as a single RGB tuple
                if "sacrifice_button" in loaded_target_rgbs:
                    self.target_rgbs["sacrifice_button"] = tuple(
                        loaded_target_rgbs["sacrifice_button"]
                    )

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
