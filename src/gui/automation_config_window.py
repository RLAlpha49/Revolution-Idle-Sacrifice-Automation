"""
Automation configuration window with simple and advanced modes for Revolution Idle Sacrifice Automation.
"""

import logging
from typing import Any, Callable, Dict, Optional

import customtkinter as ctk  # type: ignore
from .window_utils import WindowPositioner
from .advanced_setup_window import AdvancedSetupWindow

# Set up module logger
logger = logging.getLogger(__name__)


class AutomationConfigWindow:
    """Automation configuration window with simple and advanced modes."""

    def __init__(
        self,
        parent: Any,
        config_data: Dict[str, Any],
        on_start_setup_callback: Callable[[], None],
        on_config_saved_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """Initialize the automation configuration window.

        Args:
            parent: The parent widget
            config_data: The current configuration data
            on_start_setup_callback: Callback to start the setup process
            on_config_saved_callback: Callback when configuration is saved
        """
        logger.debug("Initializing automation configuration window")
        self.parent = parent
        self.config_data = config_data
        self.on_start_setup_callback = on_start_setup_callback
        self.on_config_saved_callback = on_config_saved_callback

        self.window: Optional[ctk.CTkToplevel] = None
        self.mode = "simple"  # Default to simple mode
        self.advanced_setup_window: Optional[AdvancedSetupWindow] = None

        self._create_window()

    def _create_window(self) -> None:
        """Create the automation configuration window."""
        try:
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title("Automation Configuration")
            self.window.geometry("700x600")
            self.window.minsize(650, 600)

            # Make window modal
            self.window.transient(self.parent)
            self.window.grab_set()
            self.window.protocol("WM_DELETE_WINDOW", self.close)

            # Main container with tabs
            self.main_frame = ctk.CTkFrame(self.window)
            self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Mode selection - tabs
            self.tab_view = ctk.CTkTabview(self.main_frame)
            self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

            # Add tabs
            self.simple_tab = self.tab_view.add("Simple")
            self.advanced_tab = self.tab_view.add("Advanced")

            # Set default tab
            self.tab_view.set("Simple")

            # Create content for each tab
            self._create_simple_tab()
            self._create_advanced_tab()

            # Position relative to parent window with multi-monitor support
            WindowPositioner.position_window_relative(
                self.window, self.parent, 700, 600, position="center_offset"
            )

            logger.debug("Automation configuration window created successfully")
        except (AttributeError, ValueError, RuntimeError) as e:
            logger.error(
                "Error creating automation configuration window: %s", e, exc_info=True
            )
            print(
                "Error creating automation configuration window. Check the logs for details."
            )

    def _create_simple_tab(self) -> None:
        """Create the simple mode tab content."""
        # Configuration summary frame
        summary_frame = ctk.CTkFrame(self.simple_tab)
        summary_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            summary_frame,
            text="Automation Configuration",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.pack(pady=(20, 10))

        # Configuration summary
        config_frame = ctk.CTkFrame(summary_frame)
        config_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Check if configuration exists
        has_config = self._has_valid_configuration()

        if has_config:
            # Display configuration summary
            self._display_config_summary(config_frame)

            # Button to start setup process (reconfigure)
            setup_button = ctk.CTkButton(
                summary_frame,
                text="Reconfigure",
                command=self._on_start_setup,
            )
            setup_button.pack(side="right", padx=20, pady=(0, 20))
        else:
            # Display "No configuration" message
            no_config_label = ctk.CTkLabel(
                config_frame,
                text="No automation configuration found.\nUse the Advanced tab to set up automation.",
                font=ctk.CTkFont(size=14),
                justify="center",
            )
            no_config_label.pack(expand=True)

            # Button to start setup process
            setup_button = ctk.CTkButton(
                summary_frame,
                text="Start Setup",
                command=self._on_start_setup,
            )
            setup_button.pack(side="right", padx=20, pady=(0, 20))

    def _create_advanced_tab(self) -> None:
        """Create the advanced mode tab content."""
        # Advanced configuration frame
        advanced_frame = ctk.CTkFrame(self.advanced_tab)
        advanced_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            advanced_frame,
            text="Advanced Configuration",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.pack(pady=(20, 10))

        # Description
        desc_label = ctk.CTkLabel(
            advanced_frame,
            text="Configure zodiac grid layout, rarities, and coordinates manually.",
            font=ctk.CTkFont(size=12),
            wraplength=600,
        )
        desc_label.pack(pady=(0, 20))

        # Configuration summary or setup prompt
        config_summary_frame = ctk.CTkFrame(advanced_frame)
        config_summary_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if self._has_advanced_configuration():
            # Display advanced configuration summary
            self._display_advanced_config_summary(config_summary_frame)

            # Buttons frame
            buttons_frame = ctk.CTkFrame(advanced_frame)
            buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

            # Reconfigure button
            reconfigure_button = ctk.CTkButton(
                buttons_frame,
                text="Reconfigure Advanced Setup",
                command=self._open_advanced_setup,
            )
            reconfigure_button.pack(side="left", padx=10, pady=10)

            # Switch to simple button
            switch_button = ctk.CTkButton(
                buttons_frame,
                text="Switch to Simple Mode",
                command=self._switch_to_simple,
            )
            switch_button.pack(side="right", padx=10, pady=10)
        else:
            # No advanced configuration
            no_config_label = ctk.CTkLabel(
                config_summary_frame,
                text="No advanced configuration found.\nClick 'Start Advanced Setup' to configure zodiac automation.",
                font=ctk.CTkFont(size=14),
                justify="center",
            )
            no_config_label.pack(expand=True)

            # Start advanced setup button
            setup_button = ctk.CTkButton(
                advanced_frame,
                text="Start Advanced Setup",
                command=self._open_advanced_setup,
            )
            setup_button.pack(pady=(0, 20))

    def _has_advanced_configuration(self) -> bool:
        """Check if advanced configuration exists.

        Returns:
            bool: True if advanced configuration is present
        """
        try:
            # Handle both old and new config structures
            advanced_mode_data = self.config_data.get("advanced_mode")

            # If advanced_mode is a boolean, check if it's True and look for other advanced config
            if isinstance(advanced_mode_data, bool):
                return (
                    advanced_mode_data
                    and "grid_config" in self.config_data
                    and "selected_rarities" in self.config_data
                    and "target_rgbs" in self.config_data
                )

            # If advanced_mode is a dict, use the original logic
            elif isinstance(advanced_mode_data, dict):
                return (
                    advanced_mode_data.get("advanced_mode", False)
                    and "grid_config" in advanced_mode_data
                    and "selected_rarities" in advanced_mode_data
                    and "rarity_rgbs" in advanced_mode_data
                )

            return False

        except (KeyError, TypeError, AttributeError) as e:
            logger.error("Error checking advanced configuration: %s", e, exc_info=True)
            return False

    def _display_advanced_config_summary(self, parent_frame: ctk.CTkFrame) -> None:
        """Display summary of advanced configuration.

        Args:
            parent_frame: Parent frame to add summary to
        """
        try:
            # Handle both old and new config structures
            advanced_mode_data = self.config_data.get("advanced_mode")

            # If advanced_mode is a boolean, get config from root level
            if isinstance(advanced_mode_data, bool):
                grid_config = self.config_data.get("grid_config", {})
                selected_rarities = self.config_data.get("selected_rarities", {})
                coords_available = (
                    "zodiac_coords" in self.config_data
                    and self.config_data["zodiac_coords"]
                )
            # If advanced_mode is a dict, get config from nested structure
            elif isinstance(advanced_mode_data, dict):
                grid_config = advanced_mode_data.get("grid_config", {})
                selected_rarities = advanced_mode_data.get("selected_rarities", {})
                coords_available = (
                    "zodiac_coords" in advanced_mode_data
                    and advanced_mode_data["zodiac_coords"]
                )
            else:
                # Fallback to empty config
                grid_config = {}
                selected_rarities = {}
                coords_available = False

            # Grid configuration
            grid_text = f"Grid: {grid_config.get('rows', 'N/A')}x{grid_config.get('cols', 'N/A')} ({grid_config.get('total_boxes', 'N/A')} boxes)"

            grid_label = ctk.CTkLabel(
                parent_frame, text=grid_text, font=ctk.CTkFont(size=12)
            )
            grid_label.pack(pady=5)

            # Selected rarities
            rarity_names = [
                name for name, selected in selected_rarities.items() if selected
            ]
            rarities_text = f"Rarities: {', '.join(rarity_names) if rarity_names else 'None selected'}"

            rarities_label = ctk.CTkLabel(
                parent_frame, text=rarities_text, font=ctk.CTkFont(size=12)
            )
            rarities_label.pack(pady=5)

            # Coordinates status
            coords_text = (
                f"Coordinates: {'Configured' if coords_available else 'Not configured'}"
            )

            coords_label = ctk.CTkLabel(
                parent_frame, text=coords_text, font=ctk.CTkFont(size=12)
            )
            coords_label.pack(pady=5)

        except (KeyError, TypeError, AttributeError) as e:
            logger.error(
                "Error displaying advanced config summary: %s", e, exc_info=True
            )

    def _open_advanced_setup(self) -> None:
        """Open the advanced setup window."""
        try:
            if self.advanced_setup_window:
                return  # Already open

            self.advanced_setup_window = AdvancedSetupWindow(
                self.window,
                self.config_data.get("advanced_mode", {}),
                self._on_advanced_config_saved,
                self._on_advanced_setup_cancelled,
            )
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error opening advanced setup: %s", e, exc_info=True)

    def _switch_to_simple(self) -> None:
        """Switch to simple tab."""
        try:
            self.tab_view.set("Simple")
            logger.debug("Switched to simple mode tab")
        except (AttributeError, ValueError) as e:
            logger.error("Error switching to simple mode: %s", e, exc_info=True)

    def _on_advanced_config_saved(self, config: Dict[str, Any]) -> None:
        """Handle advanced configuration being saved.

        Args:
            config: The saved configuration data
        """
        try:
            # Update the config data
            if "advanced_mode" not in self.config_data:
                self.config_data["advanced_mode"] = {}

            self.config_data["advanced_mode"].update(config)
            self.config_data["active_mode"] = "advanced"

            # Close advanced setup window
            if self.advanced_setup_window:
                self.advanced_setup_window = None

            # Refresh the UI
            self._refresh_tabs()

            # Call the config saved callback if provided
            if self.on_config_saved_callback:
                self.on_config_saved_callback(self.config_data)

            logger.info("Advanced configuration saved and UI refreshed")

        except (KeyError, TypeError, AttributeError) as e:
            logger.error("Error handling advanced config save: %s", e, exc_info=True)

    def _on_advanced_setup_cancelled(self) -> None:
        """Handle advanced setup being cancelled."""
        try:
            if self.advanced_setup_window:
                self.advanced_setup_window = None
            logger.debug("Advanced setup cancelled")
        except (AttributeError,) as e:
            logger.error("Error handling advanced setup cancel: %s", e, exc_info=True)

    def _refresh_tabs(self) -> None:
        """Refresh the tab contents."""
        try:
            # Clear and recreate tab contents
            for widget in self.simple_tab.winfo_children():
                widget.destroy()
            for widget in self.advanced_tab.winfo_children():
                widget.destroy()

            # Recreate tab contents
            self._create_simple_tab()
            self._create_advanced_tab()

            logger.debug("Refreshed tab contents")
        except (AttributeError, RuntimeError) as e:
            logger.error("Error refreshing tabs: %s", e, exc_info=True)

    def _has_valid_configuration(self) -> bool:
        """Check if a valid configuration exists."""
        try:
            # Check for simple mode configuration
            simple_config = self.config_data.get("simple_mode", {})
            has_simple = (
                "click_coords" in simple_config
                and simple_config["click_coords"]
                and "target_rgbs" not in self.config_data
                or not self.config_data["target_rgbs"]
            )

            # Check for advanced mode configuration
            has_advanced = self._has_advanced_configuration()

            return has_simple or has_advanced

        except (KeyError, TypeError, AttributeError) as e:
            logger.error("Error checking configuration validity: %s", e, exc_info=True)
            return False

    def _display_config_summary(self, parent_frame: ctk.CTkFrame) -> None:
        """Display a summary of the current configuration."""
        try:
            # Determine active mode
            active_mode = self.config_data.get("active_mode", "simple")

            # Mode label
            mode_label = ctk.CTkLabel(
                parent_frame,
                text=f"Active Mode: {active_mode.title()}",
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            mode_label.pack(pady=(10, 5))

            if active_mode == "advanced" and self._has_advanced_configuration():
                # Display advanced configuration summary
                self._display_advanced_config_summary(parent_frame)
            else:
                # Display simple configuration summary
                simple_config = self.config_data.get("simple_mode", {})
                coords_count = len(simple_config.get("click_coords", {}))
                coords_text = f"Configured coordinates: {coords_count}"

                coords_label = ctk.CTkLabel(
                    parent_frame, text=coords_text, font=ctk.CTkFont(size=12)
                )
                coords_label.pack(pady=5)

            # Add info about RGB values if available
            if "sacrifice_button" in self.config_data["target_rgbs"]:
                rgb_data = self.config_data["target_rgbs"]["sacrifice_button"]

                if isinstance(rgb_data, list) and len(rgb_data) > 0:
                    # Handle different RGB data formats
                    if isinstance(rgb_data[0], list) and len(rgb_data[0]) >= 3:
                        # Nested list format
                        rgb = rgb_data[0]
                    elif len(rgb_data) >= 3 and isinstance(rgb_data[0], (int, float)):
                        # Flat list format
                        rgb = rgb_data
                    else:
                        rgb = None

                    if rgb and len(rgb) >= 3:
                        rgb_text = (
                            f"Sacrifice Button RGB: ({rgb[0]}, {rgb[1]}, {rgb[2]})"
                        )
                        rgb_label = ctk.CTkLabel(
                            parent_frame, text=rgb_text, font=ctk.CTkFont(size=10)
                        )
                        rgb_label.pack(pady=2)

        except (KeyError, TypeError, AttributeError, IndexError) as e:
            logger.error("Error displaying config summary: %s", e, exc_info=True)

    def _on_start_setup(self) -> None:
        """Handle the start setup button click."""
        if self.on_start_setup_callback:
            self.on_start_setup_callback()
        self.close()

    def close(self) -> None:
        """Close the automation configuration window."""
        logger.debug("Closing automation configuration window")

        # Close advanced setup window if open
        if self.advanced_setup_window:
            try:
                self.advanced_setup_window.close()
                self.advanced_setup_window = None
            except (AttributeError, RuntimeError) as e:
                logger.error(
                    "Error closing advanced setup window: %s", e, exc_info=True
                )

        # Close main window
        if self.window:
            try:
                self.window.destroy()
                self.window = None
                logger.debug("Automation configuration window destroyed")
            except (AttributeError, RuntimeError) as e:
                logger.error(
                    "Error closing automation configuration window: %s",
                    e,
                    exc_info=True,
                )
                self.window = None
