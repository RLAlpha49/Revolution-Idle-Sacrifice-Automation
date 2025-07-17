"""
Help window implementation for Revolution Idle Sacrifice Automation.
"""

from typing import Any, Optional

import customtkinter as ctk  # type: ignore

from src.gui.utils import (
    create_info_label,
    create_scrollable_frame,
    create_section_header,
    open_url,
)


class HelpWindow:
    """Help window for Revolution Idle Sacrifice Automation."""

    def __init__(self, parent: Any) -> None:
        """Initialize the help window."""
        self.parent = parent
        self.window: Optional[ctk.CTkToplevel] = None
        self.tabview: Optional[ctk.CTkTabview] = None
        self._create_window()

    def _create_window(self) -> None:
        """Create the help window."""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Revolution Idle Sacrifice Automation - Help")
        self.window.geometry("800x600")
        self.window.minsize(700, 500)

        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()

        # Create tabview
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Add tabs
        self.tabview.add("Overview")
        self.tabview.add("Setup")
        self.tabview.add("Automation")
        self.tabview.add("Settings")
        self.tabview.add("Performance")

        # Create tab content
        self._create_overview_tab(self.tabview.tab("Overview"))
        self._create_setup_tab(self.tabview.tab("Setup"))
        self._create_automation_tab(self.tabview.tab("Automation"))
        self._create_settings_tab(self.tabview.tab("Settings"))
        self._create_performance_tab(self.tabview.tab("Performance"))

        # Create bottom buttons
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        github_button = ctk.CTkButton(
            button_frame,
            text="GitHub Repository",
            command=self._open_github_repo,
        )
        github_button.pack(side="left", padx=10, pady=10)

        settings_button = ctk.CTkButton(
            button_frame,
            text="Open Settings File",
            command=self._open_settings_file,
        )
        settings_button.pack(side="left", padx=10, pady=10)

        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.window.destroy,
        )
        close_button.pack(side="right", padx=10, pady=10)

    def _create_overview_tab(self, parent: Any) -> None:
        """Create the overview tab content."""
        scrollable_frame, content_frame = create_scrollable_frame(parent)

        # Title
        title = ctk.CTkLabel(
            content_frame,
            text="Revolution Idle Sacrifice Automation",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(anchor="center", pady=(10, 20))

        # Introduction
        create_section_header(content_frame, "Introduction")
        create_info_label(
            content_frame,
            "This application automates the zodiac sacrificing process in the game "
            "'Revolution Idle'. It operates in two modes: 'setup' to configure the "
            "necessary click points and colors, and 'automation' to perform the "
            "repetitive actions.",
        )

        # How it works
        create_section_header(content_frame, "How It Works")
        create_info_label(
            content_frame,
            "1. Checks the colors of all configured zodiac slots in each cycle.\n"
            "2. When any zodiac slot's color matches its target, drags that zodiac to the sacrifice box.\n"
            "3. After the drag, it checks the color of the sacrifice button.\n"
            "4. If the sacrifice button's color matches, it clicks the button and restarts the sequence.",
        )

        # Important notes
        create_section_header(content_frame, "Important Notes")
        create_info_label(
            content_frame,
            "• You can configure multiple zodiac slots during setup.\n"
            "• For consistent automation, it is recommended to auto-sell other zodiac rarities.\n"
            "• The sacrifice button's target color is hardcoded to ensure reliability.",
        )

        # Controls
        create_section_header(content_frame, "Controls")
        create_info_label(
            content_frame,
            "• Press F8 to stop automation at any time.\n"
            "• Use the Setup Mode button to configure the automation.\n"
            "• Use the Start Automation button to begin the process.",
        )

    def _create_setup_tab(self, parent: Any) -> None:
        """Create the setup tab content."""
        scrollable_frame, content_frame = create_scrollable_frame(parent)

        create_section_header(content_frame, "Setup Mode")
        create_info_label(
            content_frame,
            "Setup mode allows you to configure the positions and colors needed for automation. "
            "Follow the on-screen instructions during setup.",
        )

        create_section_header(content_frame, "Setup Process")
        create_info_label(
            content_frame,
            "1. Click on the 'Setup Mode' button to start.\n"
            "2. Follow the instructions to click on each zodiac slot.\n"
            "3. Click on the sacrifice drag box.\n"
            "4. Click on the sacrifice button.\n"
            "5. The setup will save automatically when complete.",
        )

        create_section_header(content_frame, "Tips for Setup")
        create_info_label(
            content_frame,
            "• Make sure the game window is visible during setup.\n"
            "• Position zodiacs of the desired type in the slots before setup.\n"
            "• For best results, configure the game to show only the zodiac type you want to sacrifice.",
        )

        create_section_header(content_frame, "Window Detection")
        create_info_label(
            content_frame,
            "By default, the application tries to detect the game window. If this causes issues, "
            "you can disable window detection during setup using the 'Disable Window Detection' button.",
        )

    def _create_automation_tab(self, parent: Any) -> None:
        """Create the automation tab content."""
        scrollable_frame, content_frame = create_scrollable_frame(parent)

        create_section_header(content_frame, "Automation Mode")
        create_info_label(
            content_frame,
            "Automation mode performs the repetitive actions of checking zodiac slots, "
            "dragging matching zodiacs to the sacrifice box, and clicking the sacrifice button.",
        )

        create_section_header(content_frame, "Starting Automation")
        create_info_label(
            content_frame,
            "1. Complete setup mode first.\n"
            "2. Click the 'Start Automation' button.\n"
            "3. Switch to the game window within 3 seconds.\n"
            "4. The automation will begin checking zodiac slots and performing sacrifices.",
        )

        create_section_header(content_frame, "Stopping Automation")
        create_info_label(
            content_frame,
            "• Press F8 to stop automation at any time.\n"
            "• Click the 'Stop Automation' button.\n"
            "• Close the application window.",
        )

        create_section_header(content_frame, "Troubleshooting")
        create_info_label(
            content_frame,
            "If automation is not working correctly:\n"
            "• Make sure the game window is visible and not minimized.\n"
            "• Check that the game hasn't changed visually since setup.\n"
            "• Try running setup again to reconfigure the positions and colors.",
        )

    def _create_settings_tab(self, parent: Any) -> None:
        """Create the settings tab content."""
        scrollable_frame, content_frame = create_scrollable_frame(parent)

        create_section_header(content_frame, "Settings")
        create_info_label(
            content_frame,
            "Settings are stored in the settings.py file. You can modify these settings "
            "to customize the behavior of the automation.",
        )

        create_section_header(content_frame, "Important Settings")
        create_info_label(
            content_frame,
            "• MAX_ZODIAC_SLOTS: Maximum number of zodiac slots to configure.\n"
            "• CLICK_DELAY: Delay between clicks (in seconds).\n"
            "• DRAG_DURATION: Duration of drag operations (in seconds).\n"
            "• COLOR_TOLERANCE: Tolerance for color matching (0-255).",
        )

        create_section_header(content_frame, "Advanced Settings")
        create_info_label(
            content_frame,
            "• USE_WINDOW_DETECTION: Enable/disable game window detection.\n"
            "• DEBUG_MODE: Enable/disable debug logging.\n"
            "• SACRIFICE_BUTTON_COLOR: Target color for the sacrifice button.",
        )

        create_section_header(content_frame, "Reloading Settings")
        create_info_label(
            content_frame,
            "After modifying settings, click the 'Reload Settings' button in the main window "
            "to apply the changes without restarting the application.",
        )

    def _create_performance_tab(self, parent: Any) -> None:
        """Create the performance tab content."""
        scrollable_frame, content_frame = create_scrollable_frame(parent)

        create_section_header(content_frame, "Performance Information")
        create_info_label(
            content_frame,
            "Based on testing, the script can achieve approximately 230 sacrifices per minute "
            "with 1 slot configured and the fastest possible timing settings.",
        )

        create_section_header(content_frame, "Factors Affecting Performance")
        create_info_label(
            content_frame,
            "• Number of configured zodiac slots (more slots may reduce per-slot efficiency).\n"
            "• Timing settings (CLICK_DELAY, DRAG_DURATION, etc.).\n"
            "• Computer performance and game responsiveness.\n"
            "• Game progression and visual elements.",
        )

        create_section_header(content_frame, "Optimizing Performance")
        create_info_label(
            content_frame,
            "• Configure fewer zodiac slots for faster per-slot checking.\n"
            "• Reduce timing delays if your computer can handle it.\n"
            "• Close unnecessary applications to free up system resources.\n"
            "• Use auto-sell features in the game to ensure consistent zodiac types.",
        )

        create_section_header(content_frame, "Known Limitations")
        create_info_label(
            content_frame,
            "• The script has a soft limit of about 3.8 sacrifices per second due to timing constraints.\n"
            "• Color detection may be affected by game visual changes or system color settings.\n"
            "• Window detection may not work correctly with certain system configurations.",
        )

    def _open_github_repo(self) -> None:
        """Open the GitHub repository in the default web browser."""
        open_url("https://github.com/RLAlpha49/Revolution-Idle-Sacrifice-Automation")

    def _open_settings_file(self) -> None:
        """Open the settings file in the default text editor."""
        from config.settings import CONFIG_FILE  # pylint: disable=import-outside-toplevel
        import os
        import subprocess

        try:
            os.startfile(CONFIG_FILE)
        except AttributeError:
            # For non-Windows systems
            subprocess.call(["xdg-open", CONFIG_FILE])
