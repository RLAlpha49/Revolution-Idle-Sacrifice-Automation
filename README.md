# Revolution Idle Sacrifice Automation Script

This script automates the zodiac sacrificing process in the game **Revolution Idle**. It streamlines repetitive tasks by automating mouse movements and clicks based on pixel color detection.

---

## Features

- **Two Modes:**
  - **Setup Mode:** Configure on-screen locations (coordinates) and colors for your specific computer and game resolution.
  - **Automation Mode:** Runs the automated sacrificing process using your saved configuration.
- **Configurable Settings:** Adjust delays, stop key, and message verbosity directly in the script.
- **Persistent Configuration:** Saves settings to `revolution_idle_zodiac_automation_config.json` for reuse.
- **Flexible Stop Key:** Use a character or special key (e.g., `esc`, `space`, `ctrl`) to stop automation.

---

## How it Works

The script follows this logic:

1. **Zodiac Slot Check (Click 1):** Monitors the color of a designated "Zodiac Slot".
2. **Drag Action:** If the color matches, simulates dragging the zodiac to the "Sacrifice Drag Box" (Click 2).
3. **Sacrifice Button Check (Click 3):** Checks the color of the "Sacrifice Button".
4. **Conditional Click & Restart:**
   - If the button color matches `(219, 124, 0)`, clicks the button and restarts.
   - If not, repeats the first two steps.

> [!NOTE]
> For consistent automation, auto-sell other zodiac rarities or wait for a 100% chance for an Immortal zodiac. The script relies on a consistent color at the zodiac slot.

---

## Setup and Installation

### Prerequisites

- Python 3.x
- `pynput` library (for mouse/keyboard control)
- `Pillow` library (for screen capture and pixel color detection)

### Installation

1. **Save the Script:** Download `main.py`.
2. **Install Libraries:**  

   ```sh
   pip install pynput Pillow
   ```

---

## Usage

1. **Run the Script:**  
   Navigate to the script directory and run:

   ```sh
   python main.py
   ```

2. **Select a Mode:**  
   The script presents a menu:

   ```text
   1. Setup Mode (Configure click points and colors)
   2. Automation Mode (Run the automation)
   3. Help (Learn more about the script and settings)
   4. Exit (Quit the script)
   ```

   - **1 or setup:** Guides you to set three click points:
     - Click 1: Zodiac Slot (monitor)
     - Click 2: Sacrifice Drag Box (drag target)
     - Click 3: Sacrifice Button
     - Saves configuration to `revolution_idle_zodiac_automation_config.json`.
   - **2 or automation:** Starts automation using saved config.  
     Stop with the configured STOP_KEY (default: `q`).
   - **3 or help:** Shows detailed info.
   - **4 or exit:** Quits the script.  
     (You can also press `Ctrl+C` to quit anytime.)

---

## User Configurable Settings

Edit these variables in `main.py` under "User Configurable Settings":

- `DELAY_BEFORE_CHECK`: Delay before checking pixel colors (seconds)
- `DELAY_AFTER_PRESS`: Delay after mouse press (seconds)
- `DELAY_DRAG_DURATION`: Mouse drag duration (seconds)
- `DELAY_AFTER_DRAG`: Delay after drag (seconds)
- `DELAY_AFTER_CLICK`: Delay after click (seconds)
  - *(Adjust for your computer/game responsiveness. Smaller = faster, but less reliable.)*
- `STOP_KEY`: Key to stop automation (default: `'q'`)
  - Can be a character or special key (e.g., `'esc'`, `'space'`, `'ctrl'`, etc.)
- `MESSAGE_LEVEL`: Console output verbosity
  - `'info'`: Standard messages (default)
  - `'debug'`: Detailed messages for troubleshooting

---

## Visual Guide for Click Points
