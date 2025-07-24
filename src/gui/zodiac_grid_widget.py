"""
Zodiac grid widget component for Revolution Idle Sacrifice Automation.
"""

import logging
from typing import Any, List, Tuple

import customtkinter as ctk  # type: ignore

# Set up module logger
logger = logging.getLogger(__name__)


class ZodiacGridWidget(ctk.CTkFrame):
    """Visual zodiac grid widget for advanced configuration."""

    def __init__(
        self, parent: Any, rows: int = 2, cols: int = 6, total_boxes: int = 12, **kwargs
    ) -> None:
        """Initialize the zodiac grid widget.

        Args:
            parent: Parent widget
            rows: Number of rows in the grid
            cols: Number of columns in the grid
            total_boxes: Total number of zodiac boxes to display
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)

        self.rows = rows
        self.cols = cols
        self.total_boxes = min(total_boxes, rows * cols)
        self.selected_boxes: List[bool] = [False] * self.total_boxes
        self.box_buttons: List[ctk.CTkButton] = []

        self._create_grid()

    def _create_grid(self) -> None:
        """Create the visual grid of zodiac boxes."""
        try:
            # Clear existing buttons
            for button in self.box_buttons:
                button.destroy()
            self.box_buttons.clear()

            # Create grid of buttons
            for i in range(self.total_boxes):
                row = i // self.cols
                col = i % self.cols

                button = ctk.CTkButton(
                    self,
                    text=f"{i + 1}",
                    width=50,
                    height=50,
                    command=lambda idx=i: self._toggle_box(idx),
                    fg_color="gray40",
                    hover_color="gray30",
                )
                button.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                self.box_buttons.append(button)

            # Configure grid weights for centering
            for i in range(self.cols):
                self.grid_columnconfigure(i, weight=1)
            for i in range(self.rows):
                self.grid_rowconfigure(i, weight=1)

            logger.debug("Created zodiac grid with %d boxes", self.total_boxes)
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error creating zodiac grid: %s", e, exc_info=True)

    def _toggle_box(self, index: int) -> None:
        """Toggle the selection state of a zodiac box.

        Args:
            index: Index of the box to toggle
        """
        try:
            if 0 <= index < len(self.selected_boxes):
                self.selected_boxes[index] = not self.selected_boxes[index]

                # Update button appearance
                button = self.box_buttons[index]
                if self.selected_boxes[index]:
                    button.configure(fg_color="green", hover_color="dark green")
                else:
                    button.configure(fg_color="gray40", hover_color="gray30")

                logger.debug(
                    "Toggled zodiac box %d to %s", index + 1, self.selected_boxes[index]
                )
        except (IndexError, AttributeError) as e:
            logger.error("Error toggling zodiac box: %s", e, exc_info=True)

    def update_grid(self, rows: int, cols: int, total_boxes: int) -> None:
        """Update the grid configuration.

        Args:
            rows: New number of rows
            cols: New number of columns
            total_boxes: New total number of boxes
        """
        try:
            self.rows = rows
            self.cols = cols
            self.total_boxes = min(total_boxes, rows * cols)

            # Resize selected_boxes list
            current_size = len(self.selected_boxes)
            if self.total_boxes > current_size:
                # Add new boxes (unselected by default)
                self.selected_boxes.extend([False] * (self.total_boxes - current_size))
            elif self.total_boxes < current_size:
                # Remove excess boxes
                self.selected_boxes = self.selected_boxes[: self.total_boxes]

            # Recreate the grid
            self._create_grid()

            logger.debug(
                "Updated zodiac grid to %dx%d with %d boxes", rows, cols, total_boxes
            )
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error updating zodiac grid: %s", e, exc_info=True)

    def get_selected_boxes(self) -> List[bool]:
        """Get the current selection state of all boxes.

        Returns:
            List of boolean values indicating which boxes are selected
        """
        return self.selected_boxes.copy()

    def set_selected_boxes(self, selections: List[bool]) -> None:
        """Set the selection state of all boxes.

        Args:
            selections: List of boolean values for box selection states
        """
        try:
            if len(selections) != self.total_boxes:
                logger.warning(
                    "Selection list size (%d) doesn't match total boxes (%d)",
                    len(selections),
                    self.total_boxes,
                )
                return

            self.selected_boxes = selections.copy()

            # Update button appearances
            for i, selected in enumerate(self.selected_boxes):
                if i < len(self.box_buttons):
                    button = self.box_buttons[i]
                    if selected:
                        button.configure(fg_color="green", hover_color="dark green")
                    else:
                        button.configure(fg_color="gray40", hover_color="gray30")

            logger.debug("Updated zodiac box selections")
        except (AttributeError, ValueError, TypeError, IndexError) as e:
            logger.error("Error setting zodiac box selections: %s", e, exc_info=True)

    def calculate_all_coordinates(
        self,
        corner1: Tuple[int, int],
        corner2: Tuple[int, int],
        cols: int,
        total_boxes: int,
    ) -> List[Tuple[int, int]]:
        """Calculate all zodiac box coordinates from two reference points.

        Args:
            corner1: Coordinates of the top-left corner of the first box
            corner2: Coordinates of the same corner of the box to the right and down
            cols: Number of columns in the grid
            total_boxes: Total number of boxes to calculate

        Returns:
            List of coordinate tuples for all zodiac boxes
        """
        try:
            coordinates = []

            # Calculate spacing between boxes
            x_spacing = corner2[0] - corner1[0]
            y_spacing = corner2[1] - corner1[1]

            # Generate coordinates for all boxes
            for i in range(total_boxes):
                row = i // cols
                col = i % cols

                x = corner1[0] + (col * x_spacing)
                y = corner1[1] + (row * y_spacing)

                coordinates.append((x, y))

            logger.debug(
                "Calculated %d zodiac coordinates from corners %s and %s",
                len(coordinates),
                corner1,
                corner2,
            )
            return coordinates

        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.error("Error calculating zodiac coordinates: %s", e, exc_info=True)
            return []
