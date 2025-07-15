"""
Configuration manager for Revolution Idle Sacrifice Automation Script.

This module handles loading and saving of configuration data including
click coordinates and target RGB colors for zodiac slots and sacrifice button.
"""

import json
from typing import Dict

from config.settings import CONFIG_FILE


class ConfigManager:
    """Manages configuration data for the automation script."""

    def __init__(self):
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
        except Exception as e:  # pylint: disable=broad-except
            print(f"ERROR: Error saving configuration: {e}")
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

                # Handle legacy format (for backward compatibility with old config files)
                self._handle_legacy_format(loaded_target_rgbs)

            return True

        except FileNotFoundError:
            print(
                f"Configuration file '{CONFIG_FILE}' not found. Please run in 'setup' mode first."
            )
            return False
        except json.JSONDecodeError:
            print(
                f"ERROR: Error decoding JSON from '{CONFIG_FILE}'. File might be corrupted."
            )
            return False
        except Exception as e:  # pylint: disable=broad-except
            print(f"ERROR: Error loading configuration: {e}")
            return False

    def _handle_legacy_format(self, loaded_target_rgbs: Dict) -> None:
        """Handle backward compatibility with old config file formats."""
        # Convert old single slot format to new multiple slots format
        if "rgb1" in loaded_target_rgbs and "zodiac_slots" not in self.target_rgbs:
            self.target_rgbs["zodiac_slots"] = [tuple(loaded_target_rgbs["rgb1"])]
            print("Converted legacy single zodiac slot configuration to new format.")

        if "rgb3" in loaded_target_rgbs and "sacrifice_button" not in self.target_rgbs:
            self.target_rgbs["sacrifice_button"] = tuple(loaded_target_rgbs["rgb3"])

        # Handle legacy click coordinates
        if "click1" in self.click_coords and "zodiac_slots" not in self.click_coords:
            self.click_coords["zodiac_slots"] = [self.click_coords["click1"]]

        if "click2" in self.click_coords and "sacrifice_box" not in self.click_coords:
            self.click_coords["sacrifice_box"] = self.click_coords["click2"]

        if (
            "click3" in self.click_coords
            and "sacrifice_button" not in self.click_coords
        ):
            self.click_coords["sacrifice_button"] = self.click_coords["click3"]

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
