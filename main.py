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
# 1. Checks the color of the zodiac slot.
# 2. If the color matches, it drags the zodiac to the sacrifice box.
# 3. After the drag, it checks the color of the sacrifice button.
# 4. If the sacrifice button's color matches, it clicks the button and restarts the sequence.
#    If the sacrifice button's color does NOT match, it repeats steps 1 and 2.
#
# Important Notes for Revolution Idle:
# - The first click (Click 1) should be the corner of the zodiac slot you wish to automatically sacrifice.
#   For consistent automation, it is highly recommended to auto-sell other zodiac rarities or
#   wait until you have a 100% chance for an Immortal zodiac, as the script relies on a consistent
#   color at the zodiac slot.
# - The second click (Click 2) should be the box or area where you drag the zodiac to sacrifice.
# - The third click (Click 3) is the 'Sacrifice' button. Its target color is hardcoded to (219, 124, 0)
#   to ensure reliability, as this button's color is expected to be consistent.

# --- User Configurable Settings ---
# You can easily change these values to customize the script's behavior.

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

# Message Verbosity
# Set to 'info' for standard messages. Set to 'debug' for more detailed output.
MESSAGE_LEVEL = "info"  # Options: 'info', 'debug'

# --- Global Variables (Do not modify these directly) ---
# Controller for performing mouse actions (clicks, drags, movements)
mouse = pynput.mouse.Controller()
# Flag to signal when the automation should stop
STOP_AUTOMATION = False

# Dictionary to store the captured coordinates for Click 1 (Zodiac Slot),
# Click 2 (Sacrifice Drag Box), and Click 3 (Sacrifice Button)
click_coords = {}
# Dictionary to store the target RGB colors for Click 1 (Zodiac Slot) and
# Click 3 (Sacrifice Button - hardcoded)
target_rgbs = {}

# State variable to track the setup process when in 'setup' mode
# 0: Waiting for Click 1 (Zodiac Slot)
# 1: Waiting for Click 2 (Sacrifice Drag Box)
# 2: Waiting for Click 3 (Sacrifice Button)
# 3: Setup complete
CURRENT_SETUP_STEP = 0

# Configuration file name
CONFIG_FILE = "revolution_idle_zodiac_automation_config.json"

# Global variable to store the selected mode
CURRENT_MODE = None


# --- Helper Functions ---
def get_pixel_color(x, y):
    """
    Gets the RGB color of the pixel at the given screen coordinates (x, y).
    This function requires the 'Pillow' (PIL) library to be installed.
    """
    try:
        # Take a screenshot of the entire screen
        screenshot = ImageGrab.grab()
        # Get the color of the pixel at the specified (x, y) coordinates
        pixel_color = screenshot.getpixel((x, y))
        # Return only the R, G, B components (ignore alpha channel if present)
        return pixel_color[:3]
    except Exception as e:
        show_message(
            f"ERROR: Could not get pixel color at ({x}, {y}): {e}", level="debug"
        )
        return None


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
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            click_coords = config.get("click_coords", {})
            # Convert RGB lists back to tuples for comparison
            loaded_target_rgbs = config.get("target_rgbs", {})
            target_rgbs = {k: tuple(v) for k, v in loaded_target_rgbs.items()}

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
    global CURRENT_SETUP_STEP, click_coords, target_rgbs, CURRENT_MODE

    # We only care about button presses, not releases
    if not pressed:
        return

    if CURRENT_MODE == "setup":
        if button == pynput.mouse.Button.left:
            if CURRENT_SETUP_STEP == 0:
                # Capture Click 1 coordinates (Zodiac Slot) and its current RGB color
                click_coords["click1"] = (x, y)
                target_rgbs["rgb1"] = get_pixel_color(x, y)
                show_message(
                    f"Click 1 (Zodiac Slot) captured: {click_coords['click1']} with color {target_rgbs['rgb1']}. Now left-click to set the Sacrifice Drag Box (Click 2)."
                )
                CURRENT_SETUP_STEP = 1  # Move to the next setup step
            elif CURRENT_SETUP_STEP == 1:
                # Capture Click 2 coordinates (Sacrifice Drag Box)
                click_coords["click2"] = (x, y)
                show_message(
                    f"Click 2 (Sacrifice Drag Box) captured: {click_coords['click2']}. Now left-click to set the Sacrifice Button (Click 3)."
                )
                CURRENT_SETUP_STEP = 2  # Move to the next setup step
            elif CURRENT_SETUP_STEP == 2:
                # Capture Click 3 coordinates (Sacrifice Button)
                click_coords["click3"] = (x, y)
                # Hardcoded RGB for the Sacrifice Button
                target_rgbs["rgb3"] = (219, 124, 0)
                show_message(
                    f"Click 3 (Sacrifice Button) captured: {click_coords['click3']}. Its target color is hardcoded to {target_rgbs['rgb3']}. Setup complete! Saving Revolution Idle configuration."
                )
                CURRENT_SETUP_STEP = 3  # Mark setup as complete
                save_config()  # Save the captured configuration
                # Do NOT return False here, as the listener should remain active for mode switching
        elif button == pynput.mouse.Button.right:
            show_message(
                "Right-click detected. In setup mode, please use Left-click for setup steps.",
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
    It continuously checks conditions and performs mouse actions.
    """
    global STOP_AUTOMATION, click_coords, target_rgbs

    # Ensure all necessary coordinates and RGBs are loaded
    if not all(k in click_coords for k in ["click1", "click2", "click3"]) or not all(
        k in target_rgbs for k in ["rgb1", "rgb3"]
    ):
        show_message(
            "Revolution Idle Sacrifice Automation cannot start: Missing configuration data. Please run in 'setup' mode first.",
            level="info",
        )
        return

    STOP_AUTOMATION = False  # Reset stop flag for a new automation run
    show_message(
        f"Revolution Idle Sacrifice Automation started. Press '{STOP_KEY}' to stop.", level="info"
    )

    # Loop as long as the STOP_AUTOMATION flag is not set
    while not STOP_AUTOMATION:
        time.sleep(DELAY_BEFORE_CHECK)  # Configurable delay

        # 1. Check the color at Click 1 (Zodiac Slot)
        current_rgb1 = get_pixel_color(
            click_coords["click1"][0], click_coords["click1"][1]
        )
        if current_rgb1 == target_rgbs["rgb1"]:
            show_message(
                f"Color at Zodiac Slot ({current_rgb1}) matches target ({target_rgbs['rgb1']}). Performing drag...",
                level="debug",
            )

            # 2. Hold left click and drag the mouse from Click 1 (Zodiac Slot) to Click 2 (Sacrifice Drag Box)
            mouse.position = click_coords["click1"]  # Move mouse to Zodiac Slot
            mouse.press(pynput.mouse.Button.left)
            time.sleep(DELAY_AFTER_PRESS)
            mouse.position = click_coords[
                "click2"
            ]  # Move mouse to Sacrifice Drag Box (drags the mouse)
            time.sleep(DELAY_DRAG_DURATION)
            mouse.release(pynput.mouse.Button.left)
            show_message(
                f"Dragged zodiac from {click_coords['click1']} to {click_coords['click2']}.",
                level="debug",
            )

            time.sleep(DELAY_AFTER_DRAG)

            # 3. Check the color at Click 3 (Sacrifice Button)
            current_rgb3 = get_pixel_color(
                click_coords["click3"][0], click_coords["click3"][1]
            )
            if current_rgb3 == target_rgbs["rgb3"]:
                show_message(
                    f"Color at Sacrifice Button ({current_rgb3}) matches target ({target_rgbs['rgb3']}). Clicking and restarting sequence...",
                    level="debug",
                )
                mouse.position = click_coords[
                    "click3"
                ]  # Move mouse to Sacrifice Button
                mouse.click(pynput.mouse.Button.left)
                time.sleep(DELAY_AFTER_CLICK)
            else:
                show_message(
                    f"Color at Sacrifice Button ({current_rgb3}) does NOT match target ({target_rgbs['rgb3']}). Repeating first 2 steps (check Zodiac Slot and drag).",
                    level="info",
                )
        else:
            show_message(
                f"Color at Zodiac Slot ({current_rgb1}) does NOT match target ({target_rgbs['rgb1']}). Waiting for match...",
                level="debug",
            )

    show_message(
        "Revolution Idle Sacrifice Automation loop finished. Returning to main menu.",
        level="info",
    )


# --- Setup Mode Logic ---
def run_setup_mode():
    """Handles the interactive setup process."""
    global CURRENT_SETUP_STEP, click_coords, target_rgbs

    CURRENT_SETUP_STEP = 0  # Reset for a new setup session
    show_message(
        "Entering Setup Mode for Revolution Idle. Follow the prompts to capture coordinates.",
        level="info",
    )
    show_message("1. Left-click the corner of the Zodiac Slot (Click 1).", level="info")
    show_message("2. Left-click the Sacrifice Drag Box (Click 2).", level="info")
    show_message(
        "3. Left-click the Sacrifice Button (Click 3). Note: Its target color is hardcoded to (219, 124, 0) for reliability.",
        level="info",
    )

    # Keep the setup process active until CURRENT_SETUP_STEP reaches 3
    # This loop will wait for clicks handled by on_click
    while CURRENT_SETUP_STEP < 3:
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
        that the automation will interact with. You will be prompted to
        left-click on three specific points:
        -   Click 1 (Zodiac Slot): The corner of the zodiac slot you want to sacrifice.
            The script will remember its color.
        -   Click 2 (Sacrifice Drag Box): The area where you drag the zodiac to sacrifice.
        -   Click 3 (Sacrifice Button): The 'Sacrifice' button. Its color is
            hardcoded to (219, 124, 0) for consistent detection.
        After setting these, the configuration is saved to 'revolution_idle_zodiac_automation_config.json'.

    2.  Automation Mode:
        Runs the automated sacrificing process using the saved configuration.
        The script will continuously:
        -   Check the color of the Zodiac Slot.
        -   If it matches the recorded color, it drags the zodiac to the Sacrifice Drag Box.
        -   Then, it checks the color of the Sacrifice Button.
        -   If the Sacrifice Button's color matches, it clicks it and restarts the cycle.
        -   If the Sacrifice Button's color does NOT match, it re-checks the Zodiac Slot.

    --- User Configurable Settings (Edit these in the script file) ---

    You can open the 'main.py' file in a text editor
    and modify the following variables under the 'User Configurable Settings' section:

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
    3.  Choose 'setup' (or 1) first to configure your click points.
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

    show_message("Welcome to the Revolution Idle Sacrifice Automation Script!", level="info")

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
                "Exiting Revolution Idle Sacrifice Automation Script. Goodbye!", level="info"
            )
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
