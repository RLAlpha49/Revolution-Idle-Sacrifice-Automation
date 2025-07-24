"""
Help window for Revolution Idle Sacrifice Automation.

This module provides a help window with tabs for different topics
to assist users in understanding how to use the application.
"""

import logging
import os
from typing import Any, Optional

import customtkinter as ctk
from .window_utils import WindowPositioner
from config.settings import STOP_KEY
from src.gui.utils import (
    create_info_label,
    create_scrollable_frame,
    create_section_header,
    open_url,
)

# Set up module logger
logger = logging.getLogger(__name__)


class HelpWindow:
    """Help window with tabbed information about using the application."""

    def __init__(self, parent: Any) -> None:
        """Initialize the help window."""
        try:
            self.parent = parent
            self.window: Optional[ctk.CTkToplevel] = None
            self._create_window()
            logger.debug("Help window initialized")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error initializing help window", exc_info=True)

    def _create_window(self) -> None:
        """Create the help window with tabs."""
        try:
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title("Revolution Idle Sacrifice Automation - Help")
            # Position relative to parent window with multi-monitor support
            WindowPositioner.position_window_relative(
                self.window, self.parent, 800, 600, position="center_offset"
            )  # Make the window modal

            # Create main frame
            main_frame = ctk.CTkFrame(self.window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Create title label
            title_label = ctk.CTkLabel(
                main_frame,
                text="Revolution Idle Sacrifice Automation - Help",
                font=ctk.CTkFont(size=20, weight="bold"),
            )
            title_label.pack(pady=(0, 20))

            # Create tabview
            tabview = ctk.CTkTabview(main_frame)
            tabview.pack(fill="both", expand=True)

            # Create tabs
            overview_tab = tabview.add("Overview")
            setup_tab = tabview.add("Setup")
            automation_tab = tabview.add("Automation")
            settings_tab = tabview.add("Settings")
            performance_tab = tabview.add("Performance")
            about_tab = tabview.add("About")

            # Populate tabs
            self._create_overview_tab(overview_tab)
            self._create_setup_tab(setup_tab)
            self._create_automation_tab(automation_tab)
            self._create_settings_tab(settings_tab)
            self._create_performance_tab(performance_tab)
            self._create_about_tab(about_tab)

            # Create bottom buttons frame
            button_frame = ctk.CTkFrame(main_frame)
            button_frame.pack(fill="x", pady=(20, 0))

            # Add internal padding to the button frame
            button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
            button_container.pack(fill="x", expand=True, padx=10, pady=(15, 15))

            # Create buttons
            github_button = ctk.CTkButton(
                button_container,
                text="GitHub Repository",
                command=self._open_github_repo,
                width=150,
            )
            github_button.pack(side="left", padx=10)

            settings_file_button = ctk.CTkButton(
                button_container,
                text="Open Settings File",
                command=self._open_settings_file,
                width=150,
            )
            settings_file_button.pack(side="left", padx=10)

            close_button = ctk.CTkButton(
                button_container,
                text="Close",
                command=self.window.destroy,
                width=100,
            )
            close_button.pack(side="right", padx=10)

            # Set default tab
            tabview.set("Overview")

            logger.debug("Help window created")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error creating help window", exc_info=True)
            if self.window:
                self.window.destroy()

    def _create_overview_tab(self, parent: Any) -> None:
        """Create the overview tab content."""
        try:
            scrollable_frame, content_frame = create_scrollable_frame(parent)
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

            create_section_header(
                content_frame, "Revolution Idle Sacrifice Automation"
            ).pack(anchor="w", pady=(15, 5), padx=10)
            create_info_label(
                content_frame,
                "This application automates the zodiac sacrificing process in the game "
                "'Revolution Idle'. It operates in two modes: 'setup' to configure the necessary "
                "click points and colors, and 'automation' to perform the repetitive actions.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "How It Works").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "1. Checks the colors of all configured zodiac slots in each cycle.\n"
                "2. When any zodiac slot's color matches its target, drags that zodiac to the sacrifice box.\n"
                "3. After the drag, it checks the color of the sacrifice button.\n"
                "4. If the sacrifice button's color matches, it clicks the button and restarts the sequence.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            # Important notes
            create_section_header(content_frame, "Important Notes").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "• You can configure multiple zodiac slots during setup.\n"
                "• For consistent automation, it is recommended to auto-sell other zodiac rarities.\n"
                "• The sacrifice button's target color is hardcoded to ensure reliability.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            # Controls
            create_section_header(content_frame, "Controls").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                f"• Press {STOP_KEY.upper()} to stop automation at any time.\n"
                "• Use the Setup Mode button to configure the automation.\n"
                "• Use the Start Automation button to begin the process.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            logger.debug("Overview tab created successfully")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error creating overview tab", exc_info=True)

    def _create_setup_tab(self, parent: Any) -> None:
        """Create the setup tab content."""
        try:
            scrollable_frame, content_frame = create_scrollable_frame(parent)
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

            create_section_header(content_frame, "Setup Mode").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "Setup mode allows you to configure the positions and colors needed for automation. "
                "Follow the on-screen instructions during setup.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Setup Process").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "1. Click on the 'Setup Mode' button to start.\n"
                "2. Follow the instructions to click on each zodiac slot.\n"
                "3. Click on the sacrifice drag box.\n"
                "4. Click on the sacrifice button.\n"
                "5. The setup will save automatically when complete.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Tips for Setup").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "• Make sure the game window is visible during setup.\n"
                "• Position zodiacs of the desired type in the slots before setup.\n"
                "• For best results, configure the game to show only the zodiac type you want to sacrifice.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Window Detection").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "By default, the application tries to detect the game window. If this causes issues, "
                "you can disable window detection during setup using the 'Disable Window Detection' button.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            logger.debug("Setup tab created successfully")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error creating setup tab", exc_info=True)

    def _create_automation_tab(self, parent: Any) -> None:
        """Create the automation tab content."""
        try:
            scrollable_frame, content_frame = create_scrollable_frame(parent)
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

            create_section_header(content_frame, "Automation Mode").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "Automation mode performs the repetitive actions of checking zodiac slots, "
                "dragging matching zodiacs to the sacrifice box, and clicking the sacrifice button.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Starting Automation").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "1. Complete setup mode first.\n"
                "2. Click the 'Start Automation' button.\n"
                "3. Switch to the game window within 3 seconds.\n"
                "4. The automation will begin checking zodiac slots and performing sacrifices.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Stopping Automation").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                f"• Press {STOP_KEY.upper()} to stop automation at any time.\n"
                "• Click the 'Stop Automation' button.\n"
                "• Close the application window.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Troubleshooting").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "If automation is not working correctly:\n"
                "• Make sure the game window is visible and not minimized.\n"
                "• Check that the game hasn't changed visually since setup.\n"
                "• Try running setup again to reconfigure the positions and colors.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            logger.debug("Automation tab created successfully")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error creating automation tab", exc_info=True)

    def _create_settings_tab(self, parent: Any) -> None:
        """Create the settings tab content."""
        try:
            scrollable_frame, content_frame = create_scrollable_frame(parent)
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

            create_section_header(content_frame, "Settings").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "Settings are stored in the user_settings.json file. You can modify these settings "
                "to customize the behavior of the automation.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Important Settings").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "• MAX_ZODIAC_SLOTS: Maximum number of zodiac slots to configure.\n"
                "• DELAY_AFTER_CLICK: Delay between clicks (in seconds).\n"
                "• DELAY_DRAG_DURATION: Duration of drag operations (in seconds).\n"
                "• COLOR_TOLERANCE: Tolerance for color matching (0-255).",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Advanced Settings").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "• STOP_KEY: Key to press to stop automation.\n"
                "• DEBUG_COLOR_MATCHING: Enable/disable debug color matching.\n"
                "• MESSAGE_LEVEL: Control verbosity of messages ('info' or 'debug').",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Reloading Settings").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "After modifying settings, click the 'Reload Settings' button in the main window "
                "to apply the changes without restarting the application.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            logger.debug("Settings tab created successfully")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error creating settings tab", exc_info=True)

    def _create_performance_tab(self, parent: Any) -> None:
        """Create the performance tab content."""
        try:
            scrollable_frame, content_frame = create_scrollable_frame(parent)
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

            create_section_header(content_frame, "Performance Information").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "Based on testing, the script can achieve approximately 230 sacrifices per minute "
                "with 1 slot configured and the fastest possible timing settings.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Factors Affecting Performance").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "• Number of configured zodiac slots (more slots may reduce per-slot efficiency).\n"
                "• Timing settings (DELAY_AFTER_CLICK, DELAY_DRAG_DURATION, etc.).\n"
                "• Computer performance and game responsiveness.\n"
                "• Game progression and visual elements.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Optimization Tips").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "• Configure only the zodiac slots you need for your strategy.\n"
                "• Experiment with timing settings to find the fastest reliable values.\n"
                "• Close unnecessary applications to improve performance.\n"
                "• Ensure the game is running smoothly before starting automation.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            logger.debug("Performance tab created successfully")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error creating performance tab", exc_info=True)

    def _create_about_tab(self, parent: Any) -> None:
        """Create the about tab content."""
        try:
            scrollable_frame, content_frame = create_scrollable_frame(parent)
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

            create_section_header(content_frame, "About").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "Revolution Idle Sacrifice Automation is a tool designed to automate "
                "the repetitive process of zodiac sacrificing in the game Revolution Idle.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Author").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "Created by RLAlpha49\nGitHub: https://github.com/RLAlpha49",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "Repository").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "GitHub Repository: https://github.com/RLAlpha49/Revolution-Idle-Sacrifice-Automation",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            create_section_header(content_frame, "License").pack(
                anchor="w", pady=(15, 5), padx=10
            )
            create_info_label(
                content_frame,
                "This project is licensed under the MIT License. See the LICENSE file for details.",
            ).pack(anchor="w", pady=(0, 10), padx=20)

            logger.debug("About tab created successfully")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error creating about tab", exc_info=True)

    def _open_github_repo(self) -> None:
        """Open the GitHub repository in the default web browser."""
        repo_url = "https://github.com/RLAlpha49/Revolution-Idle-Sacrifice-Automation"
        open_url(repo_url)
        logger.info("Opening GitHub repository URL")

    def _open_settings_file(self) -> None:
        """Open the settings file in the default text editor."""
        try:
            # Get the settings file path
            import subprocess  # pylint: disable=import-outside-toplevel
            import sys  # pylint: disable=import-outside-toplevel

            if hasattr(sys, "_MEIPASS"):
                # Running as compiled executable
                base_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                base_dir = os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )

            settings_file = os.path.join(base_dir, "user_settings.json")

            # Open the file with the default application
            if os.path.exists(settings_file):
                if sys.platform == "win32":
                    os.startfile(settings_file)  # pylint: disable=no-member
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", settings_file], check=True)
                else:  # Linux
                    subprocess.run(["xdg-open", settings_file], check=True)
                logger.info("Opening settings file: %s", settings_file)
            else:
                logger.warning("Settings file not found: %s", settings_file)
        except Exception:  # pylint: disable=broad-except
            logger.error("Error opening settings file", exc_info=True)
