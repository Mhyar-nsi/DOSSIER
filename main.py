"""
Mr. Robot Themed Dossier Database
A terminal-based application for creating, viewing, and editing character dossiers,
inspired by the show Mr. Robot. This script uses the curses library to create an
interactive, retro terminal interface.

Author: Mahyar
Last Modified: August 2, 2025
"""

import curses
import time
import json
import os
from curses.textpad import Textbox, rectangle
import pyfiglet

# --- Configuration & ASCII Art ---
DATA_DIR = "data"
SEPARATOR = "    ‹" + "─" * 28 + "◆" + "─" * 28 + "›"

# --- Data Handling Functions ---
def load_all_dossiers():
    """
    Scans the DATA_DIR, loads all user profiles from their respective
    profile.json files, and returns them as a list of dictionaries.

    Each user's name is derived from their folder name.

    Returns:
        list: A list of dossier dictionaries. Returns an empty list if the
              data directory doesn't exist or is empty.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        return []
    
    dossiers = []
    # Sort the directory list to ensure a consistent order.
    for user_folder in sorted(os.listdir(DATA_DIR)):
        user_path = os.path.join(DATA_DIR, user_folder)
        if os.path.isdir(user_path):
            json_path = os.path.join(user_path, "profile.json")
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # Dynamically add name and directory path to the loaded data.
                    data['name'] = user_folder.replace('_', ' ')
                    data['main_directory'] = user_path
                    dossiers.append(data)
                except (json.JSONDecodeError, KeyError):
                    # Skip any corrupted or malformed JSON files gracefully.
                    continue
    return dossiers

def get_string_in_box(stdscr, y, x, prompt, initial_text=""):
    """
    Displays a prompt and a text box for user input.

    Args:
        stdscr: The main screen window object.
        y (int): The y-coordinate for the prompt.
        x (int): The x-coordinate for the prompt.
        prompt (str): The text to display before the input box.
        initial_text (str, optional): Text to pre-populate the input box with. Defaults to "".

    Returns:
        str: The stripped string entered by the user.
    """
    stdscr.addstr(y, x, prompt, curses.color_pair(3))
    box_y, box_x = y - 1, x + len(prompt) + 1
    box_h, box_w = 3, 60

    rectangle(stdscr, box_y, box_x, box_y + box_h - 1, box_x + box_w - 1)
    stdscr.refresh()

    editwin = curses.newwin(1, box_w - 2, box_y + 1, box_x + 1)
    if initial_text:
        editwin.addstr(0, 0, initial_text)

    box = Textbox(editwin)
    box.edit()

    # Clear the entire screen after input to prevent artifacts.
    stdscr.clear()
    return box.gather().strip()


# --- UI Drawing Functions ---
def draw_ascii_banner(stdscr, text):
    """
    Draws a large ASCII art banner in the center of the screen.

    Args:
        stdscr: The main screen window object.
        text (str): The text to render as ASCII art.

    Returns:
        int: The y-coordinate immediately following the banner.
    """
    h, w = stdscr.getmaxyx()
    fig = pyfiglet.Figlet(font='slant')
    banner_lines = fig.renderText(text).split("\n")
    start_y = 1
    for i, line in enumerate(banner_lines):
        x = w // 2 - len(line) // 2
        # Ensure the line is drawn within screen bounds.
        if start_y + i < h - 1:
            stdscr.addstr(start_y + i, x, line, curses.color_pair(1))
    return start_y + len(banner_lines)

def draw_main_menu(stdscr, selected_row):
    """
    Draws the main navigation menu.

    Args:
        stdscr: The main screen window object.
        selected_row (int): The index of the currently selected menu option.
    """
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    y_after_banner = draw_ascii_banner(stdscr, "DOSSIER")
    stdscr.addstr(y_after_banner, w // 2 - len(SEPARATOR) // 2, SEPARATOR, curses.color_pair(5))
    
    menu_options = ["View Dossier Database", "Add New Dossier", "Exit"]
    for i, option in enumerate(menu_options):
        x = w // 2 - len(option) // 2
        y = y_after_banner + 3 + i
        
        attr = curses.color_pair(2) if i == selected_row else curses.A_NORMAL
        stdscr.addstr(y, x, option, attr)
        
    stdscr.refresh()

def draw_dossier_list(stdscr, current_row, entries):
    """
    Draws the scrollable list of available dossiers.

    Args:
        stdscr: The main screen window object.
        current_row (int): The index of the currently selected dossier.
        entries (list): The list of all dossier objects.
    """
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    y_after_banner = draw_ascii_banner(stdscr, "DATABASE")
    
    instructions = "Use UP/DOWN arrows. ENTER to view. 'q' to return."
    stdscr.addstr(y_after_banner + 1, w // 2 - len(instructions) // 2, instructions, curses.color_pair(3))
    
    for i, entry in enumerate(entries):
        y = y_after_banner + 4 + i
        # Prevent drawing outside the screen.
        if y >= h - 1: break
            
        display_text = f" {i+1}. {entry['name']} "
        attr = curses.color_pair(2) if i == current_row else curses.A_NORMAL
        stdscr.addstr(y, 4, display_text, attr)
        
    stdscr.refresh()

def view_dossier(stdscr, person):
    """
    Displays the detailed information for a single dossier.
    Allows navigation to the edit screen.

    Args:
        stdscr: The main screen window object.
        person (dict): The dictionary object for the selected dossier.
    """
    while True:
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        
        dossier_title = f"DOSSIER: {person.get('name', 'N/A').upper()}"
        stdscr.addstr(1, w // 2 - len(dossier_title) // 2, dossier_title, curses.color_pair(1) | curses.A_BOLD)
        
        y = 3
        stdscr.addstr(y, w // 2 - len(SEPARATOR) // 2, SEPARATOR, curses.color_pair(5))
        y += 2

        def draw_field(y, label, value, is_path=False):
            """Helper to draw a single label-value pair."""
            # Check if there's enough space to draw the field.
            if y >= h - 3: return y, True
                
            stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
            stdscr.addstr(y, 4, f"{label}:")
            stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
            
            color = curses.color_pair(4) if is_path else curses.A_NORMAL
            stdscr.addstr(y, 25, str(value or "N/A"), color)
            return y + 1, False

        # Display all fields from the person object.
        is_full = False
        fields_to_show = [
            ("Status", person.get("status")), ("Occupation", person.get("occupation")), ("Date of Birth", person.get("dob")),
            ("Last Known Address", person.get("last_known_address")), ("Phone Numbers", ", ".join(person.get("phone_numbers", []))),
            ("Emails", ", ".join(person.get("emails", []))), ("Aliases", ", ".join(person.get("aliases", []))),
            ("Last Known IP", person.get("last_known_ip")), ("Threat Level", person.get("threat_level")),
            ("Vulnerabilities", ", ".join(person.get("vulnerabilities", []))),
            ("Main Directory", person.get("main_directory"), True)
        ]
        
        for label, value, *is_path_arg in fields_to_show:
            is_path = is_path_arg[0] if is_path_arg else False
            if not is_full:
                y, is_full = draw_field(y, label, value, is_path)
        
        # Display the multi-line notes field with word wrapping.
        if not is_full:
            y += 1
            stdscr.addstr(y, 4, "Notes:", curses.color_pair(3) | curses.A_BOLD)
            y += 1
            notes_text = person.get("notes", "N/A")
            x_pos = 4
            for word in notes_text.split():
                if x_pos + len(word) >= w - 4:
                    y += 1
                    x_pos = 4
                if y >= h - 3: break
                stdscr.addstr(y, x_pos, word + " ")
                x_pos += len(word) + 1
        
        # Display navigation footer.
        nav_text = "Press 'e' to Edit | 'q' to Return"
        stdscr.addstr(h - 2, w // 2 - len(nav_text) // 2, nav_text, curses.color_pair(3))
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('e'):
            curses.curs_set(1)
            updated_person_data = dossier_form(stdscr, person)
            curses.curs_set(0)
            if updated_person_data and 'data' in updated_person_data:
                # Refresh the local person object to show immediate changes.
                person.update(updated_person_data['data'])


# --- Unified Dossier Form for Add/Edit ---
def dossier_form(stdscr, person_data=None):
    """
    A unified, scrollable form for adding a new dossier or editing an
    existing one.

    Args:
        stdscr: The main screen window object.
        person_data (dict, optional): The existing dossier data for editing.
                                      If None, the form is in 'add' mode.

    Returns:
        dict or None: A dictionary containing the saved data, or None if the
                      operation was aborted.
    """
    is_editing = person_data is not None
    
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()
    title = f"EDITING" if is_editing else "ADD NEW DOSSIER"
    
    # Define all possible fields for the form.
    fields = [
        {"label": "Full Name", "key": "name", "value": ""},
        {"label": "Subfolders", "key": "subfolders", "value": "images, logs"},
        {"label": "Status", "key": "status", "value": ""},
        {"label": "Occupation", "key": "occupation", "value": ""},
        {"label": "DOB", "key": "dob", "value": ""},
        {"label": "Address", "key": "last_known_address", "value": ""},
        {"label": "Phones (CSV)", "key": "phone_numbers", "value": ""},
        {"label": "Emails (CSV)", "key": "emails", "value": ""},
        {"label": "Aliases (CSV)", "key": "aliases", "value": ""},
        {"label": "IP Address", "key": "last_known_ip", "value": ""},
        {"label": "Threat Level", "key": "threat_level", "value": ""},
        {"label": "Vulnerabilities (CSV)", "key": "vulnerabilities", "value": ""},
        {"label": "Notes", "key": "notes", "value": ""}
    ]
    
    # If editing, pre-populate the form with existing data.
    if is_editing:
        for field in fields:
            if isinstance(person_data.get(field['key']), list):
                field['value'] = ", ".join(person_data.get(field['key'], []))
            else:
                field['value'] = person_data.get(field['key'], "")
    
    fields.append({"label": "[ Save & Exit ]", "key": "submit", "value": ""})

    current_field_index = 2 if is_editing else 0
    # Main form loop for navigation and editing.
    while True:
        stdscr.clear()
        y_after_banner = draw_ascii_banner(stdscr, title)
        
        form_start_y = y_after_banner + 1
        for i, field in enumerate(fields):
            display_y = form_start_y + i
            if display_y >= h -1: continue

            # Determine styling for the current line.
            if field['key'] == 'submit':
                line_str = f"{field['label']:^{w-8}}"
                attr = curses.color_pair(2) if i == current_field_index else curses.color_pair(6) | curses.A_BOLD
            else:
                display_value = field['value'] if len(field['value']) < 50 else field['value'][:47] + "..."
                line_str = f" {field['label']:<25}: {display_value}"
                attr = curses.color_pair(2) if i == current_field_index else curses.A_NORMAL
            
            stdscr.addstr(display_y, 4, line_str, attr)
        
        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_field_index = max(0, current_field_index - 1)
            # Prevent navigation to non-editable fields when editing.
            if is_editing and current_field_index < 2: current_field_index = len(fields) - 1
        elif key == curses.KEY_DOWN:
            current_field_index = min(len(fields) - 1, current_field_index + 1)
            # Prevent navigation to non-editable fields when editing.
            if is_editing and current_field_index < 2: current_field_index = 2
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # Exit the loop if "Save & Exit" is selected.
            if fields[current_field_index]['key'] == 'submit':
                break
            
            # Enter edit mode for the selected field.
            selected_field = fields[current_field_index]
            prompt = f"{selected_field['label']}: "
            stdscr.clear()
            draw_ascii_banner(stdscr, title)
            selected_field['value'] = get_string_in_box(stdscr, h // 2, 4, prompt, selected_field['value'])

    # --- Process and save the form data ---
    def get_list_from_str(s): return [item.strip() for item in s.split(',') if item.strip()]
    
    final_data = {}
    for field in fields:
        if field['key'] not in ['name', 'subfolders', 'submit']:
            if '(CSV)' in field['label']:
                final_data[field['key']] = get_list_from_str(field['value'])
            else:
                final_data[field['key']] = field['value']

    if is_editing:
        path = os.path.join(person_data['main_directory'], "profile.json")
    else:
        name = next(f['value'] for f in fields if f['key'] == 'name')
        if not name: return None
        
        folder_name = name.replace(' ', '_')
        user_path = os.path.join(DATA_DIR, folder_name)
        if os.path.exists(user_path): return {"error": "exists"}
        
        path = os.path.join(user_path, "profile.json")
        os.makedirs(user_path, exist_ok=True)
        subfolders_str = next(f['value'] for f in fields if f['key'] == 'subfolders')
        for subfolder in get_list_from_str(subfolders_str):
            os.makedirs(os.path.join(user_path, subfolder), exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
        
    return {"name": name if not is_editing else person_data['name'], "data": final_data}


# --- Main Application Logic ---
def dossier_viewer_loop(stdscr):
    """
    The main loop for navigating and viewing the list of dossiers.
    """
    current_row = 0
    while True:
        entries = load_all_dossiers()
        # Handle the case where no dossiers exist.
        if not entries:
            h, w = stdscr.getmaxyx()
            msg = "No dossiers found. Add one from the main menu."
            stdscr.clear()
            stdscr.addstr(h//2, w//2 - len(msg)//2, msg, curses.color_pair(3))
            stdscr.addstr(h-2, 2, "Press 'q' to return...")
            key = stdscr.getch()
            if key == ord('q'):
                break
            continue

        draw_dossier_list(stdscr, current_row, entries)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(entries) - 1:
            current_row += 1
        elif key == ord('q'):
            break 
        elif (key == curses.KEY_ENTER or key in [10, 13]) and entries:
            view_dossier(stdscr, entries[current_row])

def main(stdscr):
    """
    The main entry point for the application. Sets up the screen, colors,
    and handles the main menu navigation.

    Args:
        stdscr: The main screen window object provided by curses.wrapper.
    """
    # Hide the blinking cursor for a cleaner look.
    curses.curs_set(0)
    # Setup color pairs for the UI.
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)     # Titles
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE) # Selection highlight
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Prompts
    curses.init_pair(4, curses.COLOR_CYAN, -1)    # Paths
    curses.init_pair(5, curses.COLOR_WHITE, -1)   # Separators
    curses.init_pair(6, curses.COLOR_GREEN, -1)   # Buttons

    current_menu_row = 0
    while True:
        draw_main_menu(stdscr, current_menu_row)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_menu_row > 0:
            current_menu_row -= 1
        elif key == curses.KEY_DOWN and current_menu_row < 2:
            current_menu_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_menu_row == 0:
                dossier_viewer_loop(stdscr)
            elif current_menu_row == 1:
                dossier_form(stdscr)
            elif current_menu_row == 2:
                # Exit the application.
                break

if __name__ == "__main__":
    # The curses.wrapper handles all the low-level terminal setup and teardown,
    # ensuring the terminal is restored to its original state on exit or error.
    curses.wrapper(main)