# Ubuntu Remote Web Panel

A sleek, web-based remote control panel specifically designed to manage your Ubuntu desktop (tested on Ubuntu 24.04). It allows you to control media playback, adjust system volume, and launch various desktop applications directly from any device (like your smartphone) on the same network. 

The interface is built with an authentic Ubuntu aesthetic, complete with the Ubuntu font, color scheme, and an adaptive layout that supports both landscape and portrait orientations. It's also fully PWA-ready, meaning you can "install" it on your phone's home screen for a native app experience.

## Features

- **Media Controls (Spotify & More):** Play, pause, go to the previous or next track using `playerctl`. Displays the current playing track name.
- **System Volume Management:** Adjust your PC's audio volume using an intuitive slider (uses `wpctl` / WirePlumber).
- **Application Launcher:** Start your favorite desktop applications with a single tap. Supported apps include:
  - Spotify
  - GNOME Terminal
  - Web Browser
  - Nautilus (Files)
  - VS Code
  - OnlyOffice
  - Calculator
  - GNOME Settings
  - System Monitor
  - Screenshot Tool
  - GIMP
  - VLC
  - Discord
- **Screen Lock:** Remotely lock your GNOME session.
- **PWA Support:** Install the web app on your iOS or Android device for a fullscreen, app-like experience.

## Prerequisites

This tool is designed to run in a GNOME environment on Linux (primarily Ubuntu). It relies on standard Linux command-line utilities.

- **Python 3**
- **Flask** (Python package)
- **playerctl:** For media playback control. (`sudo apt install playerctl`)
- **WirePlumber (`wpctl`):** For volume control (standard on Ubuntu 24.04 and modern Linux distros using PipeWire).
- **GNOME Desktop Environment:** For application launching and screen locking (`dbus-send`).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ubuntu-panel.git
   cd ubuntu-panel
   ```

2. **Install Python dependencies:**
   It is recommended to use a virtual environment, but you can also install Flask globally or per-user.
   ```bash
   pip3 install Flask
   ```

3. **Ensure system dependencies are installed:**
   ```bash
   sudo apt update
   sudo apt install playerctl
   ```

## Usage

1. Start the Flask server:
   ```bash
   python3 app.py
   ```
   *(Alternatively, use the provided `iniciar_panel.sh` script if you have configured one).*

2. The server will start on port `9999`. 
3. Find your computer's local IP address (e.g., `192.168.1.50`).
4. On your smartphone or another computer on the same network, open a web browser and navigate to:
   ```
   http://YOUR_LOCAL_IP:9999
   ```

5. **To install as an App (PWA):**
   - **iOS (Safari):** Tap the Share button and select "Add to Home Screen".
   - **Android (Chrome):** Tap the three-dot menu and select "Install app" or "Add to Home screen".

## How it works

- The backend is a lightweight **Flask** server (`app.py`) that listens for API requests and executes standard Linux shell commands (`subprocess.Popen`).
- GUI applications are launched with the current `DISPLAY` environment variable so they open correctly on your active screen.
- The frontend (`templates/index.html`) is built with pure HTML/CSS/JavaScript and fetches the API endpoints asynchronously.

## License

This project is open-source and available under the MIT License.
