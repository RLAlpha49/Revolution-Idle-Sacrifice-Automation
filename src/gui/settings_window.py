"""
Settings window for Revolution Idle Sacrifice Automation.

This module provides a GUI for editing the user settings directly within the application
instead of requiring manual JSON file edits.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, Optional, Callable, List, Tuple

import customtkinter as ctk  # type: ignore

from config.settings import _settings_loader, reload_settings
from .window_utils import WindowPositioner

# Set up module logger
logger = logging.getLogger(__name__)


class SettingsWindow:
    """Settings editor window for Revolution Idle Sacrifice Automation."""

    def __init__(
        self, parent: ctk.CTk, on_settings_saved: Optional[Callable[[], None]] = None
    ) -> None:
        """
        Initialize the settings window.

        Args:
            parent: The parent window
            on_settings_saved: Callback to execute when settings are saved
        """
        self.parent = parent
        self.on_settings_saved = on_settings_saved
        self.window: Optional[ctk.CTkToplevel] = None
        self.settings_widgets: Dict[str, Any] = {}
        self.settings_values: Dict[str, Any] = {}
        self.settings_descriptions: Dict[str, str] = self._get_settings_descriptions()
        self.setting_frames: List[ctk.CTkFrame] = []
        self.slider_entries: Dict[str, Tuple[ctk.CTkSlider, ctk.CTkEntry]] = {}
        self.setting_display_names: Dict[str, str] = self._get_setting_display_names()

        self._create_window()

    def _get_setting_display_names(self) -> Dict[str, str]:
        """Get user-friendly display names for settings."""
        return {
            "color_tolerance": "Color Matching Tolerance",
            "delay_before_check": "Delay Before Color Check",
            "delay_after_press": "Delay After Mouse Press",
            "delay_drag_duration": "Mouse Drag Duration",
            "delay_after_drag": "Delay After Mouse Drag",
            "delay_after_click": "Delay After Mouse Click",
            "stop_key": "Stop Automation Key",
            "max_zodiac_slots": "Maximum Zodiac Slots",
            "debug_color_matching": "Enable Debug Color Matching",
            "message_level": "Message Verbosity Level",
            "gui_scale": "GUI Scale Factor",
        }

    def _get_settings_file_path(self) -> str:
        """Get the path to the user settings file."""
        # Get the directory where the script is running from
        if hasattr(sys, "_MEIPASS"):
            # Running as compiled executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

        return os.path.join(base_dir, "user_settings.json")

    def _get_settings_descriptions(self) -> Dict[str, str]:
        """Get descriptions for each setting."""
        return {
            "color_tolerance": "How close colors need to be to match (0 = exact match, higher = more tolerant)",
            "delay_before_check": "Delay before checking pixel colors in the automation loop (seconds)",
            "delay_after_press": "Delay immediately after a mouse press (seconds)",
            "delay_drag_duration": "Duration of the mouse drag action (seconds)",
            "delay_after_drag": "Delay after completing a drag action (seconds)",
            "delay_after_click": "Delay after performing a click action (seconds)",
            "stop_key": "Keyboard key to stop automation (e.g., 'q', 'p', 'esc', 'f1', 'space')",
            "max_zodiac_slots": "Maximum zodiac slots to configure (-1 = unlimited, positive number = limit)",
            "debug_color_matching": "Show detailed color matching info during automation",
            "message_level": "Message verbosity level ('info' or 'debug')",
            "gui_scale": "Scale factor for the GUI elements (0.8 = smaller, 1.0 = default, 1.2 = larger)",
        }

    def _create_window(self) -> None:
        """Create the settings window."""
        try:
            # Create a new top-level window
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title("Settings")
            self.window.geometry("600x700")
            self.window.minsize(500, 600)
            self.window.grab_set()  # Make window modal

            # Main frame with scrollable content
            main_frame = ctk.CTkFrame(self.window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Title
            title_label = ctk.CTkLabel(
                main_frame,
                text="Settings Editor",
                font=ctk.CTkFont(size=20, weight="bold"),
            )
            title_label.pack(pady=(0, 20))

            # Load current settings
            settings_file = self._get_settings_file_path()
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    self.settings_values = json.load(f)
                    # Filter out comment fields (keys starting with _)
                    self.settings_values = {
                        k: v
                        for k, v in self.settings_values.items()
                        if not k.startswith("_")
                    }
            except Exception as e:
                logger.error("Failed to load settings file: %s", e)
                self.settings_values = _settings_loader._get_default_settings()

            # Create scrollable frame for settings
            self.scrollable_frame = ctk.CTkScrollableFrame(main_frame)
            self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Create category frames
            self._create_categorized_settings()

            # Button frame
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(20, 0))

            # Save button
            save_button = ctk.CTkButton(
                button_frame,
                text="Save Settings",
                command=self._save_settings,
                width=150,
                height=40,
                fg_color=("green", "green"),
            )
            save_button.pack(side="left", padx=10)

            # Cancel button
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=self._close_window,
                width=150,
                height=40,
            )
            cancel_button.pack(side="right", padx=10)

            # Bind configure event to update layout
            if self.window:
                self.window.bind("<Configure>", self._on_window_configure)

            logger.debug("Settings window created")
        except Exception as e:
            logger.error("Error creating settings window: %s", e, exc_info=True)

    def _create_categorized_settings(self) -> None:
        """Create settings organized by category."""
        try:
            # Define categories and their settings
            categories = {
                "Automation Control": ["stop_key", "max_zodiac_slots"],
                "Color Detection": ["color_tolerance", "debug_color_matching"],
                "Timing Settings": [
                    "delay_before_check",
                    "delay_after_press",
                    "delay_drag_duration",
                    "delay_after_drag",
                    "delay_after_click",
                ],
                "Logging": ["message_level"],
                "Interface": ["gui_scale"],
            }

            # Create each category section
            for category, setting_keys in categories.items():
                # Create category frame
                category_frame = ctk.CTkFrame(self.scrollable_frame)
                category_frame.pack(fill="x", expand=False, padx=5, pady=10)

                # Category header
                category_label = ctk.CTkLabel(
                    category_frame,
                    text=category,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    anchor="w",
                )
                category_label.pack(fill="x", padx=10, pady=5)

                # Create settings for this category
                for key in setting_keys:
                    if key in self.settings_values:
                        self._create_setting_widget(
                            category_frame, key, self.settings_values[key]
                        )
                    elif key == "gui_scale" and key not in self.settings_values:
                        # Add GUI scale setting even if it doesn't exist yet
                        self._create_setting_widget(category_frame, key, 1.0)
                        self.settings_values[key] = 1.0

            logger.debug("Created categorized settings")
        except Exception as e:
            logger.error("Error creating categorized settings: %s", e, exc_info=True)
            # Fallback to flat list if categorization fails
            self._create_all_setting_widgets()

    def _create_all_setting_widgets(self) -> None:
        """Create all setting widgets at once to improve scrolling performance."""
        try:
            # Sort settings by type to group similar controls together
            sorted_settings = sorted(
                self.settings_values.items(),
                key=lambda x: (
                    # Order: booleans, message_level, numbers
                    0
                    if isinstance(x[1], bool)
                    else 1
                    if x[0] == "message_level"
                    else 2
                    if x[0] == "stop_key"
                    else 3
                    if isinstance(x[1], (int, float))
                    else 4
                ),
            )

            # Create all setting frames at once
            for key, value in sorted_settings:
                self._create_setting_widget(self.scrollable_frame, key, value)

            logger.debug("Created all setting widgets")
        except Exception as e:
            logger.error("Error creating setting widgets: %s", e, exc_info=True)

    def _on_window_configure(self, event: Any) -> None:
        """Handle window resize events."""
        # Update wraplength for description labels when window is resized
        try:
            new_width = max(400, event.width - 100)
            for frame in self.setting_frames:
                for child in frame.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and hasattr(child, "wraplength"):
                        child.configure(wraplength=new_width)
        except Exception as e:
            logger.error("Error handling window resize: %s", e, exc_info=True)

    def _validate_float_input(self, value: str) -> bool:
        """Validate if the input is a valid float."""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _validate_int_input(self, value: str) -> bool:
        """Validate if the input is a valid integer."""
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _entry_to_slider_sync(
        self,
        key: str,
        entry_var: ctk.StringVar,
        slider: ctk.CTkSlider,
        is_int: bool = False,
    ) -> None:
        """Sync entry value to slider."""
        try:
            value = entry_var.get()
            if value:
                if is_int:
                    slider.set(int(value))
                else:
                    slider.set(float(value))
        except Exception as e:
            logger.error(
                "Error syncing entry to slider for %s: %s", key, e, exc_info=True
            )

    def _slider_to_entry_sync(
        self,
        key: str,
        slider_value: float,
        entry_var: ctk.StringVar,
        is_int: bool = False,
    ) -> None:
        """Sync slider value to entry."""
        try:
            if is_int:
                entry_var.set(str(int(slider_value)))
            else:
                entry_var.set(f"{slider_value:.3f}")
        except Exception as e:
            logger.error(
                "Error syncing slider to entry for %s: %s", key, e, exc_info=True
            )

    def _create_setting_widget(
        self, parent: ctk.CTkFrame, key: str, value: Any
    ) -> None:
        """Create a widget for a specific setting."""
        try:
            # Create a frame for this setting
            frame = ctk.CTkFrame(parent)
            frame.pack(fill="x", expand=False, padx=5, pady=5)
            self.setting_frames.append(frame)

            # Get display name for the setting
            display_name = self.setting_display_names.get(key, key)

            # Setting label
            label = ctk.CTkLabel(
                frame,
                text=display_name,
                font=ctk.CTkFont(size=14, weight="bold"),
                width=200,
                anchor="w",
            )
            label.pack(side="top", anchor="w", padx=10, pady=(10, 0))

            # Setting description
            if key in self.settings_descriptions:
                desc_label = ctk.CTkLabel(
                    frame,
                    text=self.settings_descriptions[key],
                    font=ctk.CTkFont(size=12),
                    wraplength=500,
                    anchor="w",
                )
                desc_label.pack(side="top", anchor="w", padx=10, pady=(0, 10))

            # Create appropriate widget based on value type
            if isinstance(value, bool):
                widget = ctk.CTkSwitch(frame, text="", onvalue=True, offvalue=False)
                widget.pack(side="top", anchor="w", padx=20, pady=(0, 10))
                if value:
                    widget.select()
                else:
                    widget.deselect()
            elif key == "gui_scale":
                # Special handling for GUI scale
                # Create a frame for slider and value display
                slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
                slider_frame.pack(
                    side="top", fill="x", anchor="w", padx=20, pady=(0, 5)
                )

                # Slider for scale (0.8-1.5)
                slider = ctk.CTkSlider(
                    slider_frame, from_=0.8, to=1.5, number_of_steps=70, width=300
                )
                slider.pack(side="left", padx=(0, 10))
                slider.set(value)

                # Add entry for direct input
                entry_var = ctk.StringVar(value=f"{value:.1f}")
                entry = ctk.CTkEntry(slider_frame, width=80, textvariable=entry_var)
                entry.pack(side="left")

                # Register validation command
                entry._entry.configure(
                    validate="key",
                    validatecommand=(
                        entry._entry.register(self._validate_float_input),
                        "%P",
                    ),
                )

                # Connect slider and entry
                def update_from_slider(v: float) -> None:
                    # Round to 1 decimal place
                    rounded = round(v * 10) / 10
                    self._slider_to_entry_sync(key, rounded, entry_var)

                def update_from_entry(*args: Any) -> None:
                    self._entry_to_slider_sync(key, entry_var, slider)

                slider.configure(command=update_from_slider)
                entry_var.trace_add("write", update_from_entry)

                # Add restart note
                restart_note = ctk.CTkLabel(
                    frame,
                    text="Note: Changes to GUI scale require restarting the application",
                    font=ctk.CTkFont(size=10, slant="italic"),
                    text_color=("gray60", "gray60"),
                    anchor="w",
                )
                restart_note.pack(side="top", anchor="w", padx=20, pady=(0, 10))

                # Store both widgets for value retrieval
                widget = slider
                self.slider_entries[key] = (slider, entry)
            elif isinstance(value, (int, float)):
                if key == "max_zodiac_slots":
                    # Special handling for max_zodiac_slots
                    widget = ctk.CTkEntry(frame, width=100)
                    widget.pack(side="top", anchor="w", padx=20, pady=(0, 10))
                    widget.insert(0, str(value))
                elif key == "color_tolerance":
                    # Create a frame for slider and value display
                    slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
                    slider_frame.pack(
                        side="top", fill="x", anchor="w", padx=20, pady=(0, 5)
                    )

                    # Slider for color tolerance (0-50)
                    slider = ctk.CTkSlider(
                        slider_frame, from_=0, to=50, number_of_steps=50, width=300
                    )
                    slider.pack(side="left", padx=(0, 10))
                    slider.set(value)

                    # Add entry for direct input
                    entry_var = ctk.StringVar(value=str(int(value)))
                    entry = ctk.CTkEntry(slider_frame, width=60, textvariable=entry_var)
                    entry.pack(side="left")

                    # Register validation command
                    entry._entry.configure(
                        validate="key",
                        validatecommand=(
                            entry._entry.register(self._validate_int_input),
                            "%P",
                        ),
                    )

                    # Connect slider and entry
                    def update_from_slider(v: float) -> None:
                        self._slider_to_entry_sync(key, v, entry_var, is_int=True)

                    def update_from_entry(*args: Any) -> None:
                        self._entry_to_slider_sync(key, entry_var, slider, is_int=True)

                    slider.configure(command=update_from_slider)
                    entry_var.trace_add("write", update_from_entry)

                    # Store both widgets for value retrieval
                    widget = slider
                    self.slider_entries[key] = (slider, entry)
                else:
                    # Create a frame for slider and value display
                    slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
                    slider_frame.pack(
                        side="top", fill="x", anchor="w", padx=20, pady=(0, 5)
                    )

                    # For delay values, use a slider with small values (0-0.5)
                    slider = ctk.CTkSlider(
                        slider_frame, from_=0, to=0.5, number_of_steps=100, width=300
                    )
                    slider.pack(side="left", padx=(0, 10))
                    slider.set(value)

                    # Add entry for direct input
                    entry_var = ctk.StringVar(value=f"{value:.3f}")
                    entry = ctk.CTkEntry(slider_frame, width=80, textvariable=entry_var)
                    entry.pack(side="left")

                    # Register validation command
                    entry._entry.configure(
                        validate="key",
                        validatecommand=(
                            entry._entry.register(self._validate_float_input),
                            "%P",
                        ),
                    )

                    # Connect slider and entry
                    def update_from_slider(v: float) -> None:
                        self._slider_to_entry_sync(key, v, entry_var)

                    def update_from_entry(*args: Any) -> None:
                        self._entry_to_slider_sync(key, entry_var, slider)

                    slider.configure(command=update_from_slider)
                    entry_var.trace_add("write", update_from_entry)

                    # Store both widgets for value retrieval
                    widget = slider
                    self.slider_entries[key] = (slider, entry)
            elif key == "message_level":
                # Dropdown for message_level
                widget = ctk.CTkComboBox(frame, values=["info", "debug"], width=100)
                widget.pack(side="top", anchor="w", padx=20, pady=(0, 10))
                widget.set(value)
            else:
                # Text entry for other string values
                widget = ctk.CTkEntry(frame, width=100)
                widget.pack(side="top", anchor="w", padx=20, pady=(0, 10))
                widget.insert(0, value)

            # Store widget reference for later retrieval
            self.settings_widgets[key] = widget

            logger.debug("Created widget for setting: %s", key)
        except Exception as e:
            logger.error(
                "Error creating widget for setting %s: %s", key, e, exc_info=True
            )

    def _get_widget_value(self, key: str, widget: Any) -> Any:
        """Get the current value from a widget."""
        try:
            if isinstance(self.settings_values[key], bool):
                return widget.get() == 1
            elif isinstance(self.settings_values[key], int):
                if key == "max_zodiac_slots":
                    return int(widget.get())
                elif key == "color_tolerance":
                    # Get value from entry if it exists, otherwise from slider
                    if key in self.slider_entries:
                        entry_value = self.slider_entries[key][1].get()
                        if entry_value:
                            return int(entry_value)
                    return int(widget.get())
                else:
                    return int(float(widget.get()) * 100) / 100
            elif isinstance(self.settings_values[key], float):
                # Get value from entry if it exists, otherwise from slider
                if key in self.slider_entries:
                    entry_value = self.slider_entries[key][1].get()
                    if entry_value:
                        return float(entry_value)
                return float(widget.get())
            else:
                return widget.get()
        except Exception as e:
            logger.error(
                "Error getting value from widget for %s: %s", key, e, exc_info=True
            )
            return self.settings_values[key]  # Return original value on error

    def _save_settings(self) -> None:
        """Save settings to file."""
        try:
            # Get values from widgets
            updated_settings = {}
            scale_changed = False
            original_scale = None

            # Check if we have an original gui_scale value
            if "gui_scale" in self.settings_values:
                original_scale = self.settings_values["gui_scale"]

            for key, widget in self.settings_widgets.items():
                updated_settings[key] = self._get_widget_value(key, widget)
                if key == "gui_scale":
                    new_scale = updated_settings[key]
                    logger.info("Saving GUI scale factor: %s", new_scale)

                    # Check if scale changed
                    if (
                        original_scale is not None
                        and abs(new_scale - original_scale) > 0.01
                    ):
                        scale_changed = True
                        logger.info(
                            "GUI scale changed from %s to %s", original_scale, new_scale
                        )

            # Save to file
            settings_file = self._get_settings_file_path()
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(updated_settings, f, indent=4)

            logger.info("Settings saved to %s", settings_file)

            # Reload settings in the application
            reload_settings()

            # Call callback if provided
            if self.on_settings_saved:
                self.on_settings_saved()

            # Show success message with restart notice if scale changed
            if scale_changed:
                self._show_message(
                    "Settings saved successfully!\n\nYou changed the GUI scale factor. "
                    "Please restart the application for this change to take effect.",
                    title="Restart Required",
                )
            else:
                self._show_message("Settings saved successfully!")

            # Close window
            self._close_window()
        except Exception as e:
            logger.error("Error saving settings: %s", e, exc_info=True)
            self._show_message(f"Error saving settings: {e}", error=True)

    def _show_message(
        self, message: str, error: bool = False, title: str = "Message"
    ) -> None:
        """Show a message dialog."""
        try:
            if self.window:
                dialog = ctk.CTkToplevel(self.window)
                dialog.title(title)
                dialog.geometry("400x180")
                dialog.resizable(False, False)
                dialog.grab_set()

                # Position relative to parent window with multi-monitor support
                WindowPositioner.position_window_relative(
                    self.window, self.parent, 600, 700, position="center_offset"
                )

                # Message
                label = ctk.CTkLabel(
                    dialog,
                    text=message,
                    font=ctk.CTkFont(size=14),
                    wraplength=350,
                    justify="center",
                )
                label.pack(pady=(20, 20), expand=True)

                # OK button
                ok_button = ctk.CTkButton(
                    dialog, text="OK", command=dialog.destroy, width=100
                )
                ok_button.pack(pady=(0, 20))

                # Set focus to OK button
                ok_button.focus_set()
        except Exception as e:
            logger.error("Error showing message dialog: %s", e, exc_info=True)

    def _close_window(self) -> None:
        """Close the settings window."""
        if self.window:
            self.window.grab_release()
            self.window.destroy()
            self.window = None
            logger.debug("Settings window closed")
