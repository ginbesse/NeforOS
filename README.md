# NeforOS

NeforOS is a realistic mobile operating system shell project. It offers an experience that mimics Instagram, WhatsApp, Netflix, messaging, camera, browser, gallery, and store feeds, but operates through user interaction.

## Features

- Home screen and application launch
- Battery, storage, network, and system status
- Browser search stream
- Messaging, contact permissions, and conversation history
- Camera preview and call stream
- Gallery: image uploading, favorites, album creation
- Store-like setup flow

## Installation

### 1) Clone the repository

```bash
git clone <repo-url>
cd Nefor
```

### 2) Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the application

```bash
python app.py
```

Then go to the following address in the browser:

```text
http://127.0.0.1:8000
```

## Installation with Termux

Running it on Termux is quite easy:

```bash
pkg update && pkg upgrade
pkg install `python git
pip install -r requirements.txt
python app.py
```
Then, from a browser on your device:

```text
http://localhost:8000
```
or you can access it via your device IP.

## SYSTEM INSTALLATION AS AN SH FILE
First, go to the main folder.
cd Nefor

Secondly, run the installation script.
chmod +x install.sh start.sh

Thirdly, start the installation.
./install.sh

## Future Ideas

- Real file system support
- Media loading for camera and gallery
- More realistic application transitions
- Background services
- Deeper integration with Termux and Android devices
