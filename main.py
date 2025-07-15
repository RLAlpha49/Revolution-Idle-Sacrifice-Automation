import time
import json
import pynput.mouse
import pynput.keyboard
from PIL import ImageGrab

# --- Revolution Idle Sacrifice Automation Script ---
# This script is designed to automate the zodiac sacrificing process in the game "Revolution Idle".
# It operates in two modes: 'setup' to configure the necessary click points and colors,
# and 'automation' to perform the repetitive actions.
#
# How it works:
# 1. Checks the colors of all configured zodiac slots in each cycle.
# 2. When any zodiac slot's color matches its target, drags that zodiac to the sacrifice box.
# 3. After the drag, it checks the color of the sacrifice button.
# 4. If the sacrifice button's color matches, it clicks the button and restarts the sequence.
#    If the sacrifice button's color does NOT match, it continues checking zodiac slots.
#
# Important Notes for Revolution Idle:
# - You can configure multiple zodiac slots (unlimited by default, or limited by MAX_ZODIAC_SLOTS) during setup.
#   Each slot will have its color remembered for matching during automation.
# - For consistent automation, it is highly recommended to auto-sell other zodiac rarities or
#   wait until you have a 100% chance for the desired zodiac type, as the script relies on
#   consistent colors at the zodiac slots.
# - The sacrifice drag box should be the area where you drag zodiacs to sacrifice them.
# - The sacrifice button's target color is hardcoded to (219, 124, 0) to ensure reliability,
#   as this button's color is expected to be consistent.

# --- User Configurable Settings ---
# You can easily change these values to customize the script's behavior.

# Color Matching Tolerance
# RGB values can vary slightly due to lighting, compression, etc.
# When clicking on a zodiac slot, the RGB may darken during capture.
# The default value of 15 works well.
# This sets how close colors need to be to match (0 = exact match, higher = more tolerant)
COLOR_TOLERANCE = 15  # Allow RGB values to differ by up to 15 points per channel

# Delay Timings (in seconds)
# Adjust these if the automation is too fast or too slow for your system/game.
# These are the fastest timings I could get while keeping consistency.
DELAY_BEFORE_CHECK = 0.02  # Delay before checking pixel colors in the automation loop
DELAY_AFTER_PRESS = 0.02  # Delay immediately after a mouse press
DELAY_DRAG_DURATION = 0.02  # Duration of the mouse drag action
DELAY_AFTER_DRAG = 0.11  # Delay after completing a drag action
DELAY_AFTER_CLICK = 0.01  # Delay after performing a click action

# Automation Exit Key
# The keyboard key that will stop the automation. Default is 'q'.
# Can be a single character (e.g., 'q', 'p') or a special key name (e.g., 'esc', 'f1', 'space', 'shift', 'ctrl').
# For a list of special key names, refer to pynput.keyboard.Key documentation.
STOP_KEY = "q"

# Multiple Zodiac Slots Configuration
# Maximum number of zodiac slots that can be configured for sacrifice.
# Set this to the number of zodiac slots you want to monitor.
# Set to -1 for unlimited slots, or a positive number to limit the maximum.
# During setup, you can configure fewer slots than this maximum if desired.
MAX_ZODIAC_SLOTS = -1  # -1 = unlimited slots, or set a positive number to limit

# Debug Color Detection
# Set to True to show detailed color matching information during automation.
# This helps troubleshoot color tolerance issues.
# MESSAGE_LEVEL must be set to 'debug' to see these messages.
# Note: With unlimited zodiac slots, debug output will show all configured slots.
DEBUG_COLOR_MATCHING = False  # Set to True for detailed color matching info

# Message Verbosity
# Set to 'info' for standard messages. Set to 'debug' for more detailed output.
MESSAGE_LEVEL = "info"  # Options: 'info', 'debug'

# --- Global Variables (Do not modify these directly) ---
# Controller for performing mouse actions (clicks, drags, movements)
mouse = pynput.mouse.Controller()
# Flag to signal when the automation should stop
STOP_AUTOMATION = False

# Dictionary to store the captured coordinates for multiple Zodiac Slots,
# Sacrifice Drag Box, and Sacrifice Button
# Format: {"zodiac_slots": [(x1, y1), (x2, y2), ...], "sacrifice_box": (x, y), "sacrifice_button": (x, y)}
click_coords = {}
# Dictionary to store the target RGB colors for multiple Zodiac Slots and
# Sacrifice Button - hardcoded
# Format: {"zodiac_slots": [(r1, g1, b1), (r2, g2, b2), ...], "sacrifice_button": (r, g, b)}
target_rgbs = {}

# Counter to track the number of successful zodiac sacrifices
sacrifice_count = 0

# Performance monitoring variables
automation_start_time = 0
total_automation_time = 0
last_sacrifice_time = 0

# State variables to track the setup process when in 'setup' mode
# During setup, we first collect all zodiac slots, then the sacrifice box, then the sacrifice button
CURRENT_SETUP_STEP = (
    "zodiac_slots"  # "zodiac_slots", "sacrifice_box", "sacrifice_button", "complete"
)
ZODIAC_SLOT_COUNT = 0  # Tracks how many zodiac slots have been configured

# Configuration file name
CONFIG_FILE = "revolution_idle_zodiac_automation_config.json"

# Global variable to store the selected mode
CURRENT_MODE = None


# --- Helper Functions ---
def get_pixel_color(x, y):
    """
    Gets the RGB color of the pixel at the given screen coordinates (x, y).
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
        return pixel_color[:3]
    except Exception as e:
        show_message(
            f"ERROR: Could not get pixel color at ({x}, {y}): {e}", level="debug"
        )
        return None


def get_multiple_pixel_colors(coordinates):
    """
    Efficiently gets pixel colors for multiple coordinates in a single screenshot.
    This is much faster than multiple individual get_pixel_color calls.
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
        colors = []
        for x, y in coordinates:
            # Adjust coordinates for the region
            region_x = x - bbox[0]
            region_y = y - bbox[1]
            pixel_color = screenshot.getpixel((region_x, region_y))
            colors.append(pixel_color[:3])

        return colors
    except Exception as e:
        show_message(f"ERROR: Could not get multiple pixel colors: {e}", level="debug")
        return [None] * len(coordinates)


def colors_match(color1, color2, tolerance=COLOR_TOLERANCE):
    """
    Check if two RGB colors match within the specified tolerance.
    This makes the automation more robust against slight color variations.
    """
    if color1 is None or color2 is None:
        return False

    # Check if each RGB component is within tolerance
    return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))


def show_message(message, level="info"):
    """
    A simple console-based message display function with verbosity control.
    Messages are only printed if their level matches or is lower than MESSAGE_LEVEL.
    """
    if MESSAGE_LEVEL == "debug":
        # If debug mode, show all messages with their level prefix
        if level == "debug":
            print(f"\n--- DEBUG MESSAGE ---\n{message}\n----------------------\n")
        elif level == "info":
            print(f"\n--- INFO MESSAGE ---\n{message}\n----------------------\n")
    elif MESSAGE_LEVEL == "info" and level == "info":
        # If info mode, only show info messages without a prefix
        print(f"\n{message}\n")


def update_sacrifice_counter_display():
    """
    Updates the sacrifice counter display on the same line without creating new lines.
    """
    current_time = time.time()
    if automation_start_time > 0:
        elapsed_time = current_time - automation_start_time
        if sacrifice_count > 0:
            avg_time_per_sacrifice = elapsed_time / sacrifice_count
            sacrifices_per_minute = (
                60 / avg_time_per_sacrifice if avg_time_per_sacrifice > 0 else 0
            )
            print(
                f"\rSacrifices: {sacrifice_count} | Rate: {sacrifices_per_minute:.1f}/min | Time: {elapsed_time:.1f}s",
                end="",
                flush=True,
            )
        else:
            print(
                f"\rSacrifices: {sacrifice_count} | Time: {elapsed_time:.1f}s",
                end="",
                flush=True,
            )
    else:
        print(f"\rTotal Zodiac Sacrifices: {sacrifice_count}", end="", flush=True)


def save_config():
    """
    Saves the current click_coords and target_rgbs to a JSON file.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"click_coords": click_coords, "target_rgbs": target_rgbs}, f, indent=4
            )
        show_message(f"Revolution Idle configuration saved to {CONFIG_FILE}")
    except Exception as e:
        show_message(f"ERROR: Error saving configuration: {e}", level="info")


def load_config():
    """
    Loads click_coords and target_rgbs from a JSON file.
    Returns True if successful, False otherwise.
    """
    global click_coords, target_rgbs
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            click_coords = config.get("click_coords", {})
            # Convert RGB data back to proper format
            loaded_target_rgbs = config.get("target_rgbs", {})
            target_rgbs = {}

            # Handle zodiac_slots as a list of RGB tuples
            if "zodiac_slots" in loaded_target_rgbs:
                target_rgbs["zodiac_slots"] = [
                    tuple(rgb) for rgb in loaded_target_rgbs["zodiac_slots"]
                ]

            # Handle sacrifice_button as a single RGB tuple
            if "sacrifice_button" in loaded_target_rgbs:
                target_rgbs["sacrifice_button"] = tuple(
                    loaded_target_rgbs["sacrifice_button"]
                )

            # Handle legacy format (for backward compatibility with old config files)
            if "rgb1" in loaded_target_rgbs and "zodiac_slots" not in target_rgbs:
                # Convert old single slot format to new multiple slots format
                target_rgbs["zodiac_slots"] = [tuple(loaded_target_rgbs["rgb1"])]
                show_message(
                    "Converted legacy single zodiac slot configuration to new format."
                )

            if "rgb3" in loaded_target_rgbs and "sacrifice_button" not in target_rgbs:
                # Convert old sacrifice button format to new format
                target_rgbs["sacrifice_button"] = tuple(loaded_target_rgbs["rgb3"])

            # Handle legacy click coordinates (for backward compatibility)
            if "click1" in click_coords and "zodiac_slots" not in click_coords:
                # Convert old single slot format to new multiple slots format
                click_coords["zodiac_slots"] = [click_coords["click1"]]

            if "click2" in click_coords and "sacrifice_box" not in click_coords:
                click_coords["sacrifice_box"] = click_coords["click2"]

            if "click3" in click_coords and "sacrifice_button" not in click_coords:
                click_coords["sacrifice_button"] = click_coords["click3"]

        show_message(f"Revolution Idle configuration loaded from {CONFIG_FILE}")
        return True
    except FileNotFoundError:
        show_message(
            f"Configuration file '{CONFIG_FILE}' not found. Please run in 'setup' mode first to configure for Revolution Idle.",
            level="info",
        )
        return False
    except json.JSONDecodeError:
        show_message(
            f"ERROR: Error decoding JSON from '{CONFIG_FILE}'. File might be corrupted. Please run in 'setup' mode to re-configure for Revolution Idle.",
            level="info",
        )
        return False
    except Exception as e:
        show_message(f"ERROR: Error loading configuration: {e}", level="info")
        return False


# --- Mouse Listener Callback ---
def on_click(x, y, button, pressed):
    """
    Callback function executed when a mouse button is pressed or released.
    Behavior depends on the current mode ('setup' or 'automation').
    """
    global \
        CURRENT_SETUP_STEP, \
        ZODIAC_SLOT_COUNT, \
        click_coords, \
        target_rgbs, \
        CURRENT_MODE

    # We only care about button presses, not releases
    if not pressed:
        return

    if CURRENT_MODE == "setup":
        if button == pynput.mouse.Button.left:
            if CURRENT_SETUP_STEP == "zodiac_slots":
                # Initialize zodiac slots lists if not already done
                if "zodiac_slots" not in click_coords:
                    click_coords["zodiac_slots"] = []
                    target_rgbs["zodiac_slots"] = []

                # Capture zodiac slot coordinates and color
                click_coords["zodiac_slots"].append((x, y))
                slot_color = get_pixel_color(x, y)
                target_rgbs["zodiac_slots"].append(slot_color)
                ZODIAC_SLOT_COUNT += 1

                show_message(
                    f"Zodiac Slot {ZODIAC_SLOT_COUNT} captured: ({x}, {y}) with color {slot_color}."
                )

                if MAX_ZODIAC_SLOTS == -1:
                    # Unlimited slots - show option to continue or finish
                    show_message(
                        f"Left-click to add Zodiac Slot {ZODIAC_SLOT_COUNT + 1} (or right-click to finish adding zodiac slots and proceed to Sacrifice Drag Box)."
                    )
                elif ZODIAC_SLOT_COUNT < MAX_ZODIAC_SLOTS:
                    # Limited slots - show current count and option to continue
                    show_message(
                        f"Left-click to add Zodiac Slot {ZODIAC_SLOT_COUNT + 1} (or right-click to finish adding zodiac slots and proceed to Sacrifice Drag Box)."
                    )
                else:
                    # Reached maximum limit
                    show_message(
                        f"Maximum zodiac slots ({MAX_ZODIAC_SLOTS}) reached. Now left-click to set the Sacrifice Drag Box."
                    )
                    CURRENT_SETUP_STEP = "sacrifice_box"

            elif CURRENT_SETUP_STEP == "sacrifice_box":
                # Capture Sacrifice Drag Box coordinates
                click_coords["sacrifice_box"] = (x, y)
                show_message(
                    f"Sacrifice Drag Box captured: ({x}, {y}). Now left-click to set the Sacrifice Button."
                )
                CURRENT_SETUP_STEP = "sacrifice_button"

            elif CURRENT_SETUP_STEP == "sacrifice_button":
                # Capture Sacrifice Button coordinates
                click_coords["sacrifice_button"] = (x, y)
                # Hardcoded RGB for the Sacrifice Button
                target_rgbs["sacrifice_button"] = (219, 124, 0)
                show_message(
                    f"Sacrifice Button captured: ({x}, {y}). Its target color is hardcoded to {target_rgbs['sacrifice_button']}."
                )
                show_message(
                    f"Setup complete! Configured {len(click_coords['zodiac_slots'])} zodiac slots. Saving Revolution Idle configuration."
                )
                CURRENT_SETUP_STEP = "complete"
                save_config()  # Save the captured configuration

        elif button == pynput.mouse.Button.right:
            if CURRENT_SETUP_STEP == "zodiac_slots" and ZODIAC_SLOT_COUNT > 0:
                # User wants to finish adding zodiac slots and proceed
                show_message(
                    f"Finished adding zodiac slots. {ZODIAC_SLOT_COUNT} zodiac slots configured. Now left-click to set the Sacrifice Drag Box."
                )
                CURRENT_SETUP_STEP = "sacrifice_box"
            else:
                show_message(
                    "Right-click detected. In setup mode, right-click is only used to finish adding zodiac slots.",
                    level="info",
                )
    elif CURRENT_MODE == "automation":
        show_message(
            f"Click detected at: X={x}, Y={y}. In automation mode, clicks are performed by the script, not used for setup.",
            level="debug",
        )


# --- Keyboard Listener Callback ---
def on_press(key):
    """
    Callback function executed when a keyboard key is pressed.
    Used to detect the configured STOP_KEY to stop the automation.
    """
    global STOP_AUTOMATION
    # Only process the stop key if automation is currently running (STOP_AUTOMATION is False)
    # This prevents repeated messages when the stop key is held down or pressed multiple times
    # after automation has already ceased.
    if not STOP_AUTOMATION:
        try:
            # Check if it's a character key
            if isinstance(key, pynput.keyboard.KeyCode):
                if key.char == STOP_KEY:
                    show_message(
                        f" '{STOP_KEY}' key pressed. Stopping Revolution Idle Sacrifice Automation.",
                        level="info",
                    )
                    STOP_AUTOMATION = True
            # Check if it's a special key
            elif isinstance(key, pynput.keyboard.Key):
                if key.name == STOP_KEY:
                    show_message(
                        f" '{STOP_KEY}' key pressed. Stopping Revolution Idle Sacrifice Automation.",
                        level="info",
                    )
                    STOP_AUTOMATION = True
        except AttributeError:
            # This catch block is for unexpected key types, though unlikely with pynput.
            show_message(
                f"An unknown key type was pressed: {key}. Not the configured STOP_KEY.",
                level="debug",
            )


# --- Main Automation Logic ---
def run_automation_mode():
    """
    This function contains the core automation logic for Revolution Idle.
    It continuously checks conditions and performs mouse actions for multiple zodiac slots.
    """
    global \
        STOP_AUTOMATION, \
        click_coords, \
        target_rgbs, \
        sacrifice_count, \
        automation_start_time

    # Ensure all necessary coordinates and RGBs are loaded
    required_keys = ["zodiac_slots", "sacrifice_box", "sacrifice_button"]
    if not all(k in click_coords for k in required_keys) or not all(
        k in target_rgbs for k in ["zodiac_slots", "sacrifice_button"]
    ):
        show_message(
            "Revolution Idle Sacrifice Automation cannot start: Missing configuration data. Please run in 'setup' mode first.",
            level="info",
        )
        return

    # Verify we have at least one zodiac slot configured
    if not click_coords["zodiac_slots"] or not target_rgbs["zodiac_slots"]:
        show_message(
            "Revolution Idle Sacrifice Automation cannot start: No zodiac slots configured. Please run in 'setup' mode first.",
            level="info",
        )
        return

    STOP_AUTOMATION = False  # Reset stop flag for a new automation run
    sacrifice_count = 0  # Reset sacrifice counter for a new automation run
    automation_start_time = time.time()  # Track start time for performance statistics

    zodiac_count = len(click_coords["zodiac_slots"])
    show_message(
        f"Revolution Idle Sacrifice Automation started with {zodiac_count} zodiac slot(s). Press '{STOP_KEY}' to stop.",
        level="info",
    )

    # Display initial sacrifice counter
    update_sacrifice_counter_display()

    # Loop as long as the STOP_AUTOMATION flag is not set
    while not STOP_AUTOMATION:
        time.sleep(DELAY_BEFORE_CHECK)  # Configurable delay

        # Check all zodiac slots and sacrifice button colors in one screenshot
        coordinates_to_check = click_coords["zodiac_slots"] + [
            click_coords["sacrifice_button"]
        ]
        current_colors = get_multiple_pixel_colors(coordinates_to_check)

        if None in current_colors:
            continue  # Skip this iteration if color detection failed

        # Separate zodiac slot colors from sacrifice button color
        zodiac_colors = current_colors[:-1]

        # Check each zodiac slot for a match
        for slot_index, (current_color, target_color) in enumerate(
            zip(zodiac_colors, target_rgbs["zodiac_slots"])
        ):
            # Show color comparison for debugging (controlled by DEBUG_COLOR_MATCHING flag)
            if DEBUG_COLOR_MATCHING:
                color_diff = [
                    abs(c1 - c2) for c1, c2 in zip(current_color, target_color)
                ]
                max_diff = max(color_diff)
                show_message(
                    f"Slot {slot_index + 1}: Current={current_color}, Target={target_color}, Diff={color_diff}, MaxDiff={max_diff}, Tolerance={COLOR_TOLERANCE}, Match={colors_match(current_color, target_color)}",
                    level="debug",
                )

            if colors_match(current_color, target_color):
                slot_coords = click_coords["zodiac_slots"][slot_index]
                show_message(
                    f"✓ Zodiac Slot {slot_index + 1} matched! Current: {current_color}, Target: {target_color}. Performing drag...",
                    level="debug",
                )

                # Hold left click and drag from the zodiac slot to the sacrifice box
                mouse.position = slot_coords  # Move mouse to the matching zodiac slot
                mouse.press(pynput.mouse.Button.left)
                time.sleep(DELAY_AFTER_PRESS)
                mouse.position = click_coords["sacrifice_box"]  # Move to sacrifice box
                time.sleep(DELAY_DRAG_DURATION)
                mouse.release(pynput.mouse.Button.left)
                show_message(
                    f"Dragged zodiac from slot {slot_index + 1} {slot_coords} to sacrifice box {click_coords['sacrifice_box']}.",
                    level="debug",
                )

                time.sleep(DELAY_AFTER_DRAG)

                # Check the sacrifice button color after the drag action
                current_sacrifice_color = get_pixel_color(
                    click_coords["sacrifice_button"][0],
                    click_coords["sacrifice_button"][1],
                )
                if colors_match(
                    current_sacrifice_color, target_rgbs["sacrifice_button"]
                ):
                    show_message(
                        f"Color at Sacrifice Button ({current_sacrifice_color}) matches target ({target_rgbs['sacrifice_button']}). Clicking and restarting sequence...",
                        level="debug",
                    )
                    mouse.position = click_coords[
                        "sacrifice_button"
                    ]  # Move to sacrifice button
                    mouse.click(pynput.mouse.Button.left)
                    time.sleep(DELAY_AFTER_CLICK)

                    # Increment the sacrifice counter
                    sacrifice_count += 1
                    update_sacrifice_counter_display()

                    # Record the time of the last sacrifice
                    global last_sacrifice_time
                    last_sacrifice_time = time.time()

                    # Show detailed success message only in debug mode
                    show_message(
                        f"Zodiac from slot {slot_index + 1} sacrificed successfully! Total sacrifices: {sacrifice_count}",
                        level="debug",
                    )

                    # Break out of the zodiac slot checking loop since we've performed an action
                    break
                else:
                    show_message(
                        f"Color at Sacrifice Button ({current_sacrifice_color}) does NOT match target ({target_rgbs['sacrifice_button']}). Continuing to check other zodiac slots.",
                        level="debug",
                    )
        else:
            # This else clause executes only if no zodiac slot matched (no break occurred)
            show_message(
                "No zodiac slots have matching colors. Waiting for a match...",
                level="debug",
            )

    # Calculate and display total automation time
    global total_automation_time
    total_automation_time = time.time() - automation_start_time
    show_message(
        f"Revolution Idle Sacrifice Automation completed. Total time: {total_automation_time:.2f} seconds.",
        level="info",
    )
    # Add a newline after the counter display when automation ends
    print()


# --- Setup Mode Logic ---
def run_setup_mode():
    """Handles the interactive setup process for multiple zodiac slots."""
    global CURRENT_SETUP_STEP, ZODIAC_SLOT_COUNT, click_coords, target_rgbs

    # Reset for a new setup session
    CURRENT_SETUP_STEP = "zodiac_slots"
    ZODIAC_SLOT_COUNT = 0
    click_coords = {}
    target_rgbs = {}

    show_message(
        "Entering Setup Mode for Revolution Idle with Multiple Zodiac Slots support.",
        level="info",
    )
    if MAX_ZODIAC_SLOTS == -1:
        show_message(
            "You can configure unlimited zodiac slots for sacrifice automation.",
            level="info",
        )
    else:
        show_message(
            f"You can configure up to {MAX_ZODIAC_SLOTS} zodiac slots for sacrifice automation.",
            level="info",
        )
    show_message(
        "1. Left-click on each Zodiac Slot you want to monitor (at least 1 required).",
        level="info",
    )
    show_message(
        "2. Right-click when you're finished adding zodiac slots to proceed to the Sacrifice Drag Box.",
        level="info",
    )
    show_message(
        "3. Left-click on the Sacrifice Drag Box (where zodiacs are dragged to).",
        level="info",
    )
    show_message(
        "4. Left-click on the Sacrifice Button (its color is hardcoded for reliability).",
        level="info",
    )
    show_message("Ready to capture Zodiac Slot 1. Left-click on the first zodiac slot.")

    # Keep the setup process active until CURRENT_SETUP_STEP reaches "complete"
    # This loop will wait for clicks handled by on_click
    while CURRENT_SETUP_STEP != "complete":
        time.sleep(0.1)  # Small sleep to prevent busy-waiting

    show_message("Setup mode completed. Returning to main menu.", level="info")


# --- Help Function ---
def display_help():
    """Displays information about the script and its configurable options."""
    help_message = """
    --- Revolution Idle Sacrifice Automation Script Help ---

    This script automates the zodiac sacrificing process in Revolution Idle.
    It has two main modes:

    1.  Setup Mode:
        Allows you to define the key locations and colors on your screen
        that the automation will interact with. You will be prompted to:
        -   Left-click on multiple Zodiac Slots (unlimited by default).
            Each slot's color will be remembered for matching.
            You can configure fewer slots than the maximum if desired.
        -   Right-click when finished adding zodiac slots to proceed.
        -   Left-click on the Sacrifice Drag Box (where zodiacs are dragged).
        -   Left-click on the Sacrifice Button (color hardcoded to (219, 124, 0)).
        After setting these, the configuration is saved to 'revolution_idle_zodiac_automation_config.json'.
        
        NOTE: If you need help identifying the correct click points, check the visual guide
        in the GitHub repository at: https://github.com/RLAlpha49/Revolution-Idle-Sacrifice-Automation

    2.  Automation Mode:
        Runs the automated sacrificing process using the saved configuration.
        The script will continuously:
        -   Check the colors of all configured Zodiac Slots in each cycle.
        -   When any zodiac slot's color matches its target, drag that zodiac to the Sacrifice Box.
        -   Check the color of the Sacrifice Button after each drag.
        -   If the Sacrifice Button's color matches, click it and restart the cycle.
        -   If the Sacrifice Button's color does NOT match, continue checking zodiac slots.

    --- User Configurable Settings (Edit these in the script file) ---

    You can open the 'main.py' file in a text editor
    and modify the following variables under the 'User Configurable Settings' section:

    -   Multiple Zodiac Slots Configuration:
        -   MAX_ZODIAC_SLOTS: Maximum number of zodiac slots that can be configured.
            Set to -1 for unlimited slots (default), or a positive number to limit the maximum.
            During setup, you can configure fewer slots than this maximum if desired.

    -   Color Matching Tolerance:
        -   COLOR_TOLERANCE: Sets how close colors need to be to match (0 = exact match, higher = more tolerant).
            Allows RGB values to differ by up to X points per channel (default X=15).
            If zodiac automation only works on some slots, try increasing this value.

    -   Debug Color Detection:
        -   DEBUG_COLOR_MATCHING: Set to True to show detailed color matching information during automation.
            This helps troubleshoot color tolerance issues by showing exact RGB differences.
            Useful when zodiac slots don't match as expected.

    -   Delay Timings:
        -   DELAY_BEFORE_CHECK: Delay before checking pixel colors in the automation loop.
        -   DELAY_AFTER_PRESS: Delay immediately after a mouse press.
        -   DELAY_DRAG_DURATION: Duration of the mouse drag action.
        -   DELAY_AFTER_DRAG: Delay after completing a drag action.
        -   DELAY_AFTER_CLICK: Delay after performing a click action.
        (Adjust these values in seconds, e.g., 0.05 for 50 milliseconds)

    -   Automation Exit Key:
        -   STOP_KEY: The keyboard key that will stop the automation. Default is 'q'.
            You can set this to a single character (e.g., 'q', 'p') or a special key name.
            Common special key names include: 'esc', 'f1', 'f2', ..., 'f12', 'space',
            'enter', 'shift', 'ctrl', 'alt', 'up', 'down', 'left', 'right', etc.
            Ensure you use the exact string representation (e.g., 'esc' not 'Escape').

    -   Message Verbosity:
        -   MESSAGE_LEVEL: Controls the amount of information printed to the console.
            -   'info': Shows standard operational messages. (Default)
            -   'debug': Shows more detailed messages, useful for troubleshooting.

    --- How to Use ---
    1.  Install dependencies: `pip install pynput Pillow`
    2.  Run the script: `python main.py`
    3.  Choose 'setup' (or 1) first to configure your click points and zodiac slots.
    4.  Then, choose 'automation' (or 2) to start the process.
    5.  Press the configured STOP_KEY (default 'q') during automation to return to the main menu.
    6.  To exit the script completely, type 'exit' (or 4) in the main menu, or press Ctrl+C.
    """
    show_message(help_message, level="info")


# --- Main Execution ---
def main():
    """
    Main function to initialize listeners and manage mode switching.
    """
    global CURRENT_MODE

    show_message(
        "Welcome to the Revolution Idle Sacrifice Automation Script!", level="info"
    )

    # Attempt to load configuration at startup
    load_config()

    # Start listeners once at the beginning of the script's execution
    mouse_listener = pynput.mouse.Listener(on_click=on_click)
    keyboard_listener = pynput.keyboard.Listener(on_press=on_press)

    mouse_listener.start()
    keyboard_listener.start()

    # Main loop for mode selection
    while True:
        show_message("\nSelect an option:", level="info")
        print("1. Setup Mode (Configure click points and colors)")
        print("2. Automation Mode (Run the automation)")
        print("3. Help (Learn more about the script and settings)")
        print("4. Exit (Quit the script)")
        mode_choice = (
            input("Enter your choice (1/setup, 2/automation, 3/help, 4/exit): ")
            .lower()
            .strip()
        )

        if mode_choice in ["1", "setup"]:
            CURRENT_MODE = "setup"
            run_setup_mode()
        elif mode_choice in ["2", "automation"]:
            CURRENT_MODE = "automation"
            run_automation_mode()
        elif mode_choice in ["3", "help"]:
            display_help()
        elif mode_choice in ["4", "exit"]:
            show_message(
                "Exiting Revolution Idle Sacrifice Automation Script. Goodbye!",
                level="info",
            )
            # Stop the listeners before exiting
            mouse_listener.stop()
            keyboard_listener.stop()
            break  # Exit the main loop
        else:
            show_message(
                "Invalid choice. Please enter '1', 'setup', '2', 'automation', '3', 'help', '4', or 'exit'.",
                level="info",
            )

        # Reset CURRENT_MODE to None after a mode finishes, so the loop prompts again
        CURRENT_MODE = None

    # These joins will only be reached if the main loop is explicitly broken (e.g., via 'exit' or Ctrl+C)
    # They ensure the listener threads are properly cleaned up when the script exits.
    mouse_listener.join()
    keyboard_listener.join()

    show_message("Script execution finished.", level="info")


if __name__ == "__main__":
    main()
