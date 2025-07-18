"""
Utility functions for color detection and matching.

This module provides functions for capturing pixel colors from the screen
and comparing colors with tolerance for the automation script.
"""

from typing import List, Optional, Tuple

from PIL import ImageGrab

from config.settings import COLOR_TOLERANCE


def get_pixel_color(x: int, y: int) -> Optional[Tuple[int, int, int]]:
    """
    Gets the RGB color of the pixel at the given screen coordinates (x, y).

    Args:
        x: X coordinate on screen
        y: Y coordinate on screen

    Returns:
        Tuple of RGB values (r, g, b) or None if error occurs
    """
    try:
        # Take a small region screenshot instead of full screen for better performance
        # This is much faster than capturing the entire screen
        region_size = 5  # 5x5 pixel region around the target
        left = max(0, x - region_size)
        top = max(0, y - region_size)
        right = x + region_size
        bottom = y + region_size

        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))

        # Adjust coordinates for the smaller region
        region_x = x - left
        region_y = y - top

        # Get the color of the pixel at the specified coordinates
        pixel_color = screenshot.getpixel((region_x, region_y))
        # Return only the R, G, B components (ignore alpha channel if present)
        if isinstance(pixel_color, (tuple, list)) and len(pixel_color) >= 3:
            return (int(pixel_color[0]), int(pixel_color[1]), int(pixel_color[2]))

        print(f"ERROR: Unexpected pixel color format: {pixel_color}")
        return None
    except OSError as e:
        print(f"ERROR: Could not capture screenshot: {e}")
        return None
    except IndexError as e:
        print(f"ERROR: Pixel coordinates out of bounds: {e}")
        return None
    except ValueError as e:
        print(f"ERROR: Invalid pixel data: {e}")
        return None


def get_multiple_pixel_colors(
    coordinates: List[Tuple[int, int]],
) -> List[Optional[Tuple[int, int, int]]]:
    """
    Efficiently gets pixel colors for multiple coordinates in a single screenshot.
    This is much faster than multiple individual get_pixel_color calls.

    Args:
        coordinates: List of (x, y) coordinate tuples

    Returns:
        List of RGB tuples or None values if errors occur
    """
    try:
        if not coordinates:
            return []

        # Find bounding box that contains all coordinates
        min_x = min(coord[0] for coord in coordinates)
        max_x = max(coord[0] for coord in coordinates)
        min_y = min(coord[1] for coord in coordinates)
        max_y = max(coord[1] for coord in coordinates)

        # Add small padding
        padding = 5
        bbox = (min_x - padding, min_y - padding, max_x + padding, max_y + padding)

        # Take single screenshot of the region
        screenshot = ImageGrab.grab(bbox=bbox)

        # Get colors for all coordinates
        colors: List[Optional[Tuple[int, int, int]]] = []
        for x, y in coordinates:
            # Adjust coordinates for the region
            region_x = x - bbox[0]
            region_y = y - bbox[1]
            pixel_color = screenshot.getpixel((region_x, region_y))

            # Handle different pixel color formats
            if isinstance(pixel_color, (tuple, list)) and len(pixel_color) >= 3:
                colors.append(
                    (int(pixel_color[0]), int(pixel_color[1]), int(pixel_color[2]))
                )
            else:
                colors.append(None)

        return colors
    except OSError as e:
        print(f"ERROR: Could not capture screenshot: {e}")
        return [None] * len(coordinates)
    except IndexError as e:
        print(f"ERROR: Pixel coordinates out of bounds: {e}")
        return [None] * len(coordinates)
    except ValueError as e:
        print(f"ERROR: Invalid pixel data: {e}")
        return [None] * len(coordinates)


def colors_match(
    color1: Optional[Tuple[int, int, int]],
    color2: Optional[Tuple[int, int, int]],
    tolerance: int = COLOR_TOLERANCE,
) -> bool:
    """
    Check if two RGB colors match within the specified tolerance.
    This makes the automation more robust against slight color variations.

    Args:
        color1: First RGB color tuple
        color2: Second RGB color tuple
        tolerance: Maximum difference allowed per RGB component

    Returns:
        True if colors match within tolerance, False otherwise
    """
    if color1 is None or color2 is None:
        return False

    # Check if each RGB component is within tolerance
    return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))
