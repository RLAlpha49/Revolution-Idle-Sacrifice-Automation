"""
Advanced setup window for configuring zodiac grid and rarities in Revolution Idle Sacrifice Automation.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

import customtkinter as ctk  # type: ignore
import pygetwindow as gw  # type: ignore
import pynput.mouse  # type: ignore

from utils.color_utils import get_pixel_color
from .zodiac_config import ZODIAC_RARITIES
from .zodiac_grid_widget import ZodiacGridWidget
from .window_utils import WindowPositioner

# Set up module logger
logger = logging.getLogger(__name__)


class AdvancedSetupWindow:
    """Advanced setup window for configuring zodiac grid and rarities."""

    def __init__(
        self,
        parent: Any,
        config_data: Dict[str, Any],
        save_callback: Callable[[Dict[str, Any]], None],
        cancel_callback: Callable[[], None],
    ) -> None:
        """Initialize the advanced setup window.

        Args:
            parent: Parent widget
            config_data: Current configuration data
            save_callback: Callback to save configuration
            cancel_callback: Callback when setup is cancelled
        """
        logger.debug("Initializing advanced setup window")
        self.parent = parent
        self.config_data = config_data or {}
        self.save_callback = save_callback
        self.cancel_callback = cancel_callback

        self.window: Optional[ctk.CTkToplevel] = None

        # Grid configuration
        self.rows_var = ctk.IntVar(value=2)
        self.cols_var = ctk.IntVar(value=6)
        self.total_boxes_var = ctk.IntVar(value=12)

        # Setup state
        self.setup_phase = "grid_config"
        self.corner_clicks: List[Tuple[int, int]] = []
        self.calculated_coords: List[Tuple[int, int]] = []

        # Other coordinates
        self.sacrifice_box_coords: Optional[Tuple[int, int]] = None
        self.sacrifice_button_coords: Optional[Tuple[int, int]] = None

        # Rarity selection
        self.selected_rarities: Dict[str, bool] = {
            rarity: False for rarity in ZODIAC_RARITIES
        }

        # Widgets
        self.zodiac_grid: Optional[ZodiacGridWidget] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.instructions_label: Optional[ctk.CTkLabel] = None
        self.rarity_checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        self.setup_button: Optional[ctk.CTkButton] = None
        self.save_button: Optional[ctk.CTkButton] = None

        # Coordinate capture state
        self.mouse_listener: Optional[pynput.mouse.Listener] = None
        self.capture_window: Optional[ctk.CTkToplevel] = None
        self.window_detection_enabled = True

        self._create_window()

    def _create_window(self) -> None:
        """Create the advanced setup window with scrollable content."""
        try:
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title("Advanced Zodiac Setup")
            self.window.geometry("900x700")
            self.window.minsize(800, 600)

            # Make window modal
            self.window.transient(self.parent)
            self.window.grab_set()
            self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)

            # Main container
            main_container = ctk.CTkFrame(self.window)
            main_container.pack(fill="both", expand=True, padx=10, pady=10)

            # Create scrollable frame
            self.scrollable_frame = ctk.CTkScrollableFrame(
                main_container,
                label_text="Advanced Zodiac Configuration",
                label_font=ctk.CTkFont(size=16, weight="bold"),
            )
            self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Create the UI sections in the scrollable frame
            self._create_header(self.scrollable_frame)
            self._create_grid_config_section(self.scrollable_frame)
            self._create_rarity_section(self.scrollable_frame)
            self._create_setup_section(self.scrollable_frame)

            # Create buttons in the main container (not scrollable)
            button_frame = ctk.CTkFrame(main_container)
            button_frame.pack(fill="x", padx=5, pady=(5, 0))
            self._create_buttons(button_frame)

            # Position the window relative to parent with multi-monitor support
            self._center_window()

            logger.debug(
                "Advanced setup window created successfully with scrollable content"
            )
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error creating advanced setup window: %s", e, exc_info=True)

    def _create_header(self, parent: ctk.CTkFrame) -> None:
        """Create the header section."""
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Advanced Zodiac Automation Setup",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(
            header_frame,
            text="Configure grid layout and rarities",
            font=ctk.CTkFont(size=14),
        )
        self.status_label.pack(pady=(0, 10))

    def _create_grid_config_section(self, parent: ctk.CTkFrame) -> None:
        """Create the grid configuration section."""
        config_frame = ctk.CTkFrame(parent)
        config_frame.pack(fill="x", padx=10, pady=5)

        # Title
        config_title = ctk.CTkLabel(
            config_frame,
            text="Grid Configuration",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        config_title.pack(pady=(10, 5))

        # Grid controls
        controls_frame = ctk.CTkFrame(config_frame)
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Rows
        ctk.CTkLabel(controls_frame, text="Rows:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        rows_entry = ctk.CTkEntry(controls_frame, textvariable=self.rows_var, width=60)
        rows_entry.grid(row=0, column=1, padx=5, pady=5)

        # Columns
        ctk.CTkLabel(controls_frame, text="Columns:").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )
        cols_entry = ctk.CTkEntry(controls_frame, textvariable=self.cols_var, width=60)
        cols_entry.grid(row=0, column=3, padx=5, pady=5)

        # Total boxes
        ctk.CTkLabel(controls_frame, text="Total Boxes:").grid(
            row=0, column=4, padx=5, pady=5, sticky="w"
        )
        total_entry = ctk.CTkEntry(
            controls_frame, textvariable=self.total_boxes_var, width=60
        )
        total_entry.grid(row=0, column=5, padx=5, pady=5)

        # Update button
        update_button = ctk.CTkButton(
            controls_frame, text="Update Grid", command=self._update_grid
        )
        update_button.grid(row=0, column=6, padx=10, pady=5)

        # Grid preview
        grid_frame = ctk.CTkFrame(config_frame)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        grid_label = ctk.CTkLabel(
            grid_frame, text="Grid Preview (click boxes to select):"
        )
        grid_label.pack(pady=(10, 5))

        # Create zodiac grid widget
        self.zodiac_grid = ZodiacGridWidget(
            grid_frame,
            rows=self.rows_var.get(),
            cols=self.cols_var.get(),
            total_boxes=self.total_boxes_var.get(),
        )
        self.zodiac_grid.pack(pady=(0, 10))

    def _create_rarity_section(self, parent: ctk.CTkFrame) -> None:
        """Create the rarity selection section."""
        rarity_frame = ctk.CTkFrame(parent)
        rarity_frame.pack(fill="x", padx=10, pady=5)

        rarity_title = ctk.CTkLabel(
            rarity_frame,
            text="Select Rarities to Automate",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        rarity_title.pack(pady=(10, 5))

        # Create checkboxes for each rarity
        checkboxes_frame = ctk.CTkFrame(rarity_frame)
        checkboxes_frame.pack(fill="x", padx=10, pady=(0, 10))

        for i, rarity in enumerate(ZODIAC_RARITIES.keys()):
            checkbox = ctk.CTkCheckBox(
                checkboxes_frame,
                text=rarity,
                command=lambda r=rarity: self._toggle_rarity(r),
            )
            checkbox.grid(row=i // 5, column=i % 5, padx=10, pady=5, sticky="w")
            self.rarity_checkboxes[rarity] = checkbox

    def _create_setup_section(self, parent: ctk.CTkFrame) -> None:
        """Create the setup instructions section."""
        setup_frame = ctk.CTkFrame(parent)
        setup_frame.pack(fill="x", padx=10, pady=5)

        setup_title = ctk.CTkLabel(
            setup_frame,
            text="Coordinate Setup",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        setup_title.pack(pady=(10, 5))

        self.instructions_label = ctk.CTkLabel(
            setup_frame,
            text="Click 'Start Coordinate Setup' to begin capturing zodiac positions.",
            wraplength=800,
        )
        self.instructions_label.pack(pady=(0, 10))

        self.setup_button = ctk.CTkButton(
            setup_frame,
            text="Start Coordinate Setup",
            command=self._start_coordinate_setup,
        )
        self.setup_button.pack(pady=(0, 10))

    def _create_buttons(self, parent: ctk.CTkFrame) -> None:
        """Create the action buttons."""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame, text="Cancel", command=self._on_cancel
        )
        cancel_button.pack(side="left", padx=10, pady=10)

        # Save button (initially disabled)
        self.save_button = ctk.CTkButton(
            button_frame,
            text="Save Configuration",
            command=self._save_configuration,
            state="disabled",
        )
        self.save_button.pack(side="right", padx=10, pady=10)

    def _center_window(self) -> None:
        """Position the window relative to parent with multi-monitor support."""
        try:
            # Position relative to parent window with multi-monitor support
            WindowPositioner.position_window_relative(
                self.window, self.parent, 900, 700, position="center_offset"
            )
            logger.debug("Advanced setup window positioned relative to parent")
        except (AttributeError, ValueError) as e:
            logger.error(
                "Error positioning advanced setup window: %s", e, exc_info=True
            )
            # Fallback to screen center
            WindowPositioner.center_on_screen(self.window, 900, 700)

    def _update_grid(self) -> None:
        """Update the zodiac grid based on current settings."""
        try:
            rows = max(1, self.rows_var.get())
            cols = max(1, self.cols_var.get())
            total_boxes = max(1, min(self.total_boxes_var.get(), rows * cols))

            # Update the variables to reflect valid values
            self.rows_var.set(rows)
            self.cols_var.set(cols)
            self.total_boxes_var.set(total_boxes)

            if self.zodiac_grid:
                self.zodiac_grid.update_grid(rows, cols, total_boxes)

            logger.debug("Updated grid to %dx%d with %d boxes", rows, cols, total_boxes)
        except (ValueError, AttributeError, TypeError) as e:
            logger.error("Error updating grid: %s", e, exc_info=True)

    def _toggle_rarity(self, rarity: str) -> None:
        """Toggle a rarity selection.

        Args:
            rarity: Name of the rarity to toggle
        """
        try:
            if rarity in self.selected_rarities:
                checkbox = self.rarity_checkboxes[rarity]
                self.selected_rarities[rarity] = checkbox.get() == 1
                logger.debug(
                    "Toggled rarity %s to %s", rarity, self.selected_rarities[rarity]
                )
        except (KeyError, AttributeError) as e:
            logger.error("Error toggling rarity %s: %s", rarity, e, exc_info=True)

    def _start_coordinate_setup(self) -> None:
        """Start the coordinate setup process."""
        try:
            # Validate grid configuration
            if self.total_boxes_var.get() < 2:
                self._show_error("At least 2 zodiac boxes are required for setup.")
                return

            # Validate rarity selection
            if not any(self.selected_rarities.values()):
                self._show_error("Please select at least one rarity to sacrifice.")
                return

            # Check if Revolution Idle game is running before starting coordinate capture
            if not self._check_revolution_idle_running():
                self._show_error(
                    "Revolution Idle game not detected!\n\n"
                    "Please make sure the Revolution Idle game is running before starting coordinate setup.\n"
                    "The setup process requires the game window to be open to capture coordinates and colors."
                )
                return

            # Hide window and start coordinate capture
            if self.window:
                self.window.withdraw()
            self.setup_phase = "corner_clicks"
            self.corner_clicks.clear()

            # Start the advanced coordinate capture
            self._start_advanced_coordinate_capture()

        except (ValueError, AttributeError) as e:
            logger.error("Error starting coordinate setup: %s", e, exc_info=True)

    def _start_advanced_coordinate_capture(self) -> None:
        """Start the advanced coordinate capture process."""
        try:
            # Create a capture instruction window
            self._create_capture_window()

            # Start mouse listener
            self.mouse_listener = pynput.mouse.Listener(
                on_click=self._on_coordinate_click
            )
            self.mouse_listener.start()

            logger.debug("Advanced coordinate capture started")

        except (AttributeError, OSError) as e:
            logger.error("Error starting coordinate capture: %s", e, exc_info=True)
            self._restore_main_window()

    def _create_capture_window(self) -> None:
        """Create the coordinate capture instruction window."""
        try:
            self.capture_window = ctk.CTkToplevel()
            self.capture_window.title("Advanced Coordinate Capture")
            self.capture_window.geometry("600x400")
            self.capture_window.attributes("-topmost", True)

            # Make window stay on top and modal-like
            self.capture_window.transient(None)
            self.capture_window.grab_set()

            # Main frame
            main_frame = ctk.CTkFrame(self.capture_window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Title
            title_label = ctk.CTkLabel(
                main_frame,
                text="Advanced Zodiac Coordinate Setup",
                font=ctk.CTkFont(size=18, weight="bold"),
            )
            title_label.pack(pady=(10, 20))

            # Instructions text (will be updated based on phase)
            self.instructions_label = ctk.CTkLabel(
                main_frame,
                text="",
                wraplength=550,
                justify="left",
                font=ctk.CTkFont(size=12),
            )
            self.instructions_label.pack(pady=(0, 20), fill="both", expand=True)

            # Update instructions for current phase
            self._update_capture_instructions()

            # Buttons frame
            button_frame = ctk.CTkFrame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))

            # Cancel button
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel Setup",
                command=self._cancel_coordinate_capture,
                fg_color="red",
                hover_color="dark red",
            )
            cancel_button.pack(side="left", padx=5)

            # Disable window detection button
            disable_detection_button = ctk.CTkButton(
                button_frame,
                text="Disable Window Detection",
                command=self._disable_window_detection,
            )
            disable_detection_button.pack(side="right", padx=5)

            logger.debug("Capture window created")

        except (AttributeError, ValueError, RuntimeError) as e:
            logger.error("Error creating capture window: %s", e, exc_info=True)

    def _update_capture_instructions(self) -> None:
        """Update the capture instructions based on current phase."""
        try:
            if not self.instructions_label:
                return

            if self.setup_phase == "corner_clicks":
                if len(self.corner_clicks) == 0:
                    text = """Step 1: First Zodiac Box Corner\n\nClick on the TOP-LEFT CORNER of the FIRST zodiac box.\n\nThis will be used as the reference point for calculating all other zodiac box positions.\n\nMake sure you click on a consistent corner (top-left is recommended)."""
                elif len(self.corner_clicks) == 1:
                    text = """Step 2: Reference Zodiac Box Corner\n\nClick on the TOP-LEFT CORNER of a zodiac box that is:\n- One column to the RIGHT and one row DOWN from the first box\n\nThis helps calculate the spacing between zodiac boxes."""
            elif self.setup_phase == "sacrifice_box":
                text = """Step 3: Sacrifice Box\n\nClick on the CENTER of the Sacrifice Box.\n\nThis is where zodiac items will be placed before sacrificing."""
            elif self.setup_phase == "sacrifice_button":
                text = """Step 4: Sacrifice Button\n\nClick on the CENTER of the Sacrifice Button.\n\nThis button will be clicked to perform the sacrifice action."""
            else:
                text = "Unknown setup phase"

            self.instructions_label.configure(text=text)
            logger.debug("Updated capture instructions for phase: %s", self.setup_phase)

        except (AttributeError, ValueError) as e:
            logger.error("Error updating capture instructions: %s", e, exc_info=True)

    def _on_coordinate_click(
        self, x: int, y: int, button: pynput.mouse.Button, pressed: bool
    ) -> None:
        """Handle mouse clicks during coordinate capture."""
        try:
            if not pressed or button != pynput.mouse.Button.left:
                return

            # Check if click is on Revolution Idle window (if detection enabled)
            if self.window_detection_enabled and not self._is_click_on_revolution_idle(
                x, y
            ):
                logger.debug("Click ignored - not on Revolution Idle window")
                return

            logger.info(
                "Coordinate click captured: (%d, %d) in phase %s",
                x,
                y,
                self.setup_phase,
            )

            # Handle different setup phases
            if self.setup_phase == "corner_clicks":
                self._handle_corner_click(x, y)
            elif self.setup_phase == "sacrifice_box":
                self._handle_sacrifice_box_click(x, y)
            elif self.setup_phase == "sacrifice_button":
                self._handle_sacrifice_button_click(x, y)

        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error handling coordinate click: %s", e, exc_info=True)

    def _handle_corner_click(self, x: int, y: int) -> None:
        """Handle corner clicks for zodiac box reference points."""
        try:
            self.corner_clicks.append((x, y))
            logger.info(
                "Corner click %d captured: (%d, %d)", len(self.corner_clicks), x, y
            )

            if len(self.corner_clicks) == 2:
                # Calculate all zodiac coordinates
                if self.zodiac_grid:
                    self.calculated_coords = self.zodiac_grid.calculate_all_coordinates(
                        self.corner_clicks[0],
                        self.corner_clicks[1],
                        self.cols_var.get(),
                        self.total_boxes_var.get(),
                    )
                    logger.info(
                        "Calculated %d zodiac coordinates", len(self.calculated_coords)
                    )

                # Move to next phase
                self.setup_phase = "sacrifice_box"

            # Update instructions
            self._update_capture_instructions()

        except (AttributeError, ValueError) as e:
            logger.error("Error handling corner click: %s", e, exc_info=True)

    def _handle_sacrifice_box_click(self, x: int, y: int) -> None:
        """Handle sacrifice box click."""
        try:
            self.sacrifice_box_coords = (x, y)
            logger.info("Sacrifice box captured: (%d, %d)", x, y)

            # Move to next phase
            self.setup_phase = "sacrifice_button"
            self._update_capture_instructions()

        except (AttributeError, ValueError) as e:
            logger.error("Error handling sacrifice box click: %s", e, exc_info=True)

    def _handle_sacrifice_button_click(self, x: int, y: int) -> None:
        """Handle sacrifice button click."""
        try:
            self.sacrifice_button_coords = (x, y)

            # Capture RGB color of the sacrifice button
            button_color = get_pixel_color(x, y)
            logger.info(
                "Sacrifice button captured: (%d, %d) with color %s", x, y, button_color
            )

            # Complete the coordinate capture
            self._complete_coordinate_capture()

        except (AttributeError, ValueError, OSError) as e:
            logger.error("Error handling sacrifice button click: %s", e, exc_info=True)

    def _complete_coordinate_capture(self) -> None:
        """Complete the coordinate capture process."""
        try:
            # Stop mouse listener
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None

            # Close capture window
            if self.capture_window:
                self.capture_window.destroy()
                self.capture_window = None

            # Restore main window
            self._restore_main_window()

            # Enable save button
            if self.save_button:
                self.save_button.configure(state="normal")

            # Update status
            if self.status_label:
                self.status_label.configure(
                    text="Coordinate capture completed! Ready to save configuration."
                )

            logger.info("Coordinate capture completed successfully")

        except (AttributeError, OSError) as e:
            logger.error("Error completing coordinate capture: %s", e, exc_info=True)

    def _cancel_coordinate_capture(self) -> None:
        """Cancel the coordinate capture process."""
        try:
            # Stop mouse listener
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None

            # Close capture window
            if self.capture_window:
                self.capture_window.destroy()
                self.capture_window = None

            # Restore main window
            self._restore_main_window()

            # Reset capture state
            self.setup_phase = "grid_config"
            self.corner_clicks.clear()
            self.calculated_coords.clear()
            self.sacrifice_box_coords = None
            self.sacrifice_button_coords = None

            logger.info("Coordinate capture cancelled")

        except (AttributeError, OSError) as e:
            logger.error("Error cancelling coordinate capture: %s", e, exc_info=True)

    def _disable_window_detection(self) -> None:
        """Disable window detection for coordinate capture."""
        self.window_detection_enabled = False
        logger.info("Window detection disabled for coordinate capture")

    def _restore_main_window(self) -> None:
        """Restore the main setup window."""
        try:
            if self.window:
                self.window.deiconify()
                self.window.lift()
                self.window.focus_set()
        except (AttributeError, RuntimeError) as e:
            logger.error("Error restoring main window: %s", e, exc_info=True)

    def _check_revolution_idle_running(self) -> bool:
        """Check if Revolution Idle game is currently running.

        Returns:
            bool: True if Revolution Idle window is found, False otherwise.
        """
        try:
            # Get all windows and check each one strictly
            all_windows = gw.getAllWindows()

            game_windows = []
            for window in all_windows:
                window_title = window.title.strip()

                # Only accept windows with EXACTLY "Revolution Idle" as the title
                if window_title == "Revolution Idle":
                    # Additional validation: check if window has reasonable game dimensions
                    try:
                        width = window.width
                        height = window.height

                        if width >= 400 and height >= 300:
                            game_windows.append(window)
                            logger.debug(
                                "Found valid Revolution Idle game window: '%s' (%dx%d)",
                                window_title,
                                width,
                                height,
                            )
                        else:
                            logger.debug(
                                "Skipping small window '%s' (%dx%d) - likely not the game",
                                window_title,
                                width,
                                height,
                            )
                    except (AttributeError, TypeError):
                        logger.debug(
                            "Skipping window '%s' - cannot get dimensions", window_title
                        )
                        continue
                else:
                    # Log any window that contains "Revolution Idle" but doesn't match exactly
                    if "revolution idle" in window_title.lower():
                        logger.debug(
                            "Skipping non-exact match: '%s' (not exactly 'Revolution Idle')",
                            window_title,
                        )

            if game_windows:
                logger.info(
                    "Revolution Idle game detected - %d valid game window(s) found",
                    len(game_windows),
                )
                return True
            else:
                logger.warning(
                    "No Revolution Idle game windows found (must be exactly titled 'Revolution Idle')"
                )
                return False

        except Exception as e:
            logger.error(
                "Error checking for Revolution Idle game: %s", e, exc_info=True
            )
            # If there's an error detecting windows, be conservative and assume game is NOT running
            return False

    def _is_click_on_revolution_idle(self, x: int, y: int) -> bool:
        """Check if a click is on the Revolution Idle window using strict detection."""
        try:
            # Get all windows and check each one strictly
            all_windows = gw.getAllWindows()

            for window in all_windows:
                window_title = window.title.strip()

                # Only accept windows with EXACTLY "Revolution Idle" as the title
                if window_title == "Revolution Idle":
                    # Additional validation: check if window has reasonable game dimensions
                    try:
                        width = window.width
                        height = window.height

                        if width >= 400 and height >= 300:
                            # Check if click is within this valid game window
                            if (
                                window.left <= x <= window.right
                                and window.top <= y <= window.bottom
                            ):
                                logger.debug(
                                    "Click on valid Revolution Idle game window: '%s' (%dx%d)",
                                    window_title,
                                    width,
                                    height,
                                )
                                return True
                        else:
                            logger.debug(
                                "Skipping small window '%s' (%dx%d) - likely not the game",
                                window_title,
                                width,
                                height,
                            )
                    except (AttributeError, TypeError):
                        logger.debug(
                            "Skipping window '%s' - cannot get dimensions", window_title
                        )
                        continue
                else:
                    # Log any window that contains "Revolution Idle" but doesn't match exactly
                    if "revolution idle" in window_title.lower():
                        logger.debug(
                            "Skipping non-exact match: '%s' (not exactly 'Revolution Idle')",
                            window_title,
                        )

            logger.debug("Click not on any valid Revolution Idle game window")
            return False

        except (AttributeError, OSError, RuntimeError) as e:
            logger.error("Error checking window for click: %s", e, exc_info=True)
            return True  # Default to allowing clicks if detection fails

    def _save_configuration(self) -> None:
        """Save the current configuration."""
        try:
            # Build configuration data
            config: Dict[str, Any] = {
                "grid_config": {
                    "rows": self.rows_var.get(),
                    "cols": self.cols_var.get(),
                    "total_boxes": self.total_boxes_var.get(),
                },
                "selected_boxes": self.zodiac_grid.get_selected_boxes()
                if self.zodiac_grid
                else [],
                "selected_rarities": {
                    k: v for k, v in self.selected_rarities.items() if v
                },
                "rarity_rgbs": {
                    k: v
                    for k, v in ZODIAC_RARITIES.items()
                    if self.selected_rarities.get(k, False)
                },
                "advanced_mode": True,
            }

            # Add coordinate data if available
            if self.calculated_coords:
                config["zodiac_coords"] = self.calculated_coords

                # Convert to the format expected by the automation engine
                config["click_coords"] = {
                    "zodiac_slots": self.calculated_coords,
                }

                # Add target RGB data for zodiac slots (using selected rarities)
                # Store unique RGB values based on selected rarities instead of duplicating
                selected_rarity_rgbs = [
                    ZODIAC_RARITIES[rarity]
                    for rarity in self.selected_rarities.keys()
                    if self.selected_rarities[rarity]
                ]
                if selected_rarity_rgbs:
                    # Store unique RGB values for selected rarities
                    config["target_rgbs"] = {"zodiac_slots": selected_rarity_rgbs}
                    logger.debug(
                        "Stored %d unique RGB values for zodiac slots: %s",
                        len(selected_rarity_rgbs),
                        selected_rarity_rgbs,
                    )

            if self.sacrifice_box_coords:
                config["sacrifice_box"] = self.sacrifice_box_coords
                if "click_coords" not in config:
                    config["click_coords"] = {}
                config["click_coords"]["sacrifice_box"] = [self.sacrifice_box_coords]

            if self.sacrifice_button_coords:
                config["sacrifice_button"] = self.sacrifice_button_coords
                if "click_coords" not in config:
                    config["click_coords"] = {}
                config["click_coords"]["sacrifice_button"] = [
                    self.sacrifice_button_coords
                ]

                # Add sacrifice button RGB (captured during setup)
                button_color = get_pixel_color(*self.sacrifice_button_coords)
                if button_color:
                    if "target_rgbs" not in config:
                        config["target_rgbs"] = {}
                    config["target_rgbs"]["sacrifice_button"] = [button_color]

            # Call save callback
            if self.save_callback is not None:
                self.save_callback(config)

            self.close()
            logger.info("Advanced configuration saved successfully")
        except (AttributeError, ValueError, TypeError, KeyError) as e:
            logger.error("Error saving configuration: %s", e, exc_info=True)
            self._show_error("Failed to save configuration. Check logs for details.")

    def _show_error(self, message: str) -> None:
        """Show an error message dialog.

        Args:
            message: Error message to display
        """
        error_window = ctk.CTkToplevel(self.window)
        error_window.title("Error")
        error_window.geometry("400x150")
        error_window.transient(self.window)
        error_window.grab_set()

        label = ctk.CTkLabel(error_window, text=message, wraplength=350)
        label.pack(pady=20, padx=20, expand=True)

        button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
        button.pack(pady=10)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        logger.info("Advanced setup cancelled by user")
        if self.cancel_callback is not None:
            self.cancel_callback()
        self.close()

    def close(self) -> None:
        """Close the advanced setup window."""
        logger.debug("Closing advanced setup window")

        # Clean up coordinate capture resources
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
                self.mouse_listener = None
            except (AttributeError, RuntimeError) as e:
                logger.error("Error stopping mouse listener: %s", e, exc_info=True)

        if self.capture_window:
            try:
                self.capture_window.destroy()
                self.capture_window = None
            except (AttributeError, RuntimeError) as e:
                logger.error("Error closing capture window: %s", e, exc_info=True)

        # Close main window
        if self.window:
            try:
                self.window.destroy()
                self.window = None
                logger.debug("Advanced setup window destroyed")
            except (AttributeError, RuntimeError) as e:
                logger.error(
                    "Error closing advanced setup window: %s", e, exc_info=True
                )
                self.window = None
