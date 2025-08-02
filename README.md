# DOSSIER - Mr. Robot Themed Dossier Database

*Control is an illusion.*

A terminal-based dossier database application inspired by the show **Mr. Robot**. This script uses Python and the `curses` library to create an interactive, retro terminal interface for managing character profiles.

---

## ◆ About The Project

This project is a tribute to the aesthetics and themes of the TV show *Mr. Robot*. It provides a command-line interface (CLI) to create, view, and edit dossiers. All data is stored locally in `json` files, organized into directories for each subject, mimicking a hacker's private intelligence database.

**Built With:**
* [Python 3](https://www.python.org/)
* [curses](https://docs.python.org/3/howto/curses.html)
* [pyfiglet](https://github.com/pwaller/pyfiglet)

---

## ◆ Features

* **Retro Terminal UI:** A fully interactive, menu-driven interface built with `curses`.
* **Create, View, and Edit Dossiers:** Manage all your subjects' information seamlessly.
* **Dynamic Data Handling:** Dossiers are loaded dynamically from a structured `data` directory.
* **ASCII Art:** Thematic banners powered by `pyfiglet` for an authentic feel.
* **Persistent Storage:** All dossier information is saved locally in easy-to-read `profile.json` files.
* **Keyboard Navigation:** Navigate the entire application using only your keyboard, just like a real terminal power user.

---

## ◆ Prerequisites

Make sure you have Python 3 installed on your system. You will also need `pip` to install the project dependencies.

* **Python 3**
* **pip**

---

## ◆ Installation & Usage

Follow these steps to get the application running on your local machine.

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/Mhyar-nsi/DOSSIER.git](https://github.com/Mhyar-nsi/DOSSIER.git)
    cd DOSSIER
    ```

2.  **Install the required Python libraries:**
    ```sh
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```sh
    python main.py
    ```

---

## ◆ File Structure

The application uses a simple directory structure to store data. All dossiers are located inside the `data/` directory, which is created automatically if it doesn't exist.