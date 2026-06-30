# event-intelligent offline package

This package is designed for a Windows computer without Python, Node.js, npm, pip, or project dependencies installed.

## Files

- `install_offline.bat`: checks that the offline package is complete and prepares local folders.
- `start_event_intelligent.bat`: starts the app.
- `app\event-intelligent-server.exe`: bundled backend executable.
- `app\meeting_assistant.db`: SQLite database copied from the build machine when available.
- `app\uploads`: uploaded files copied from the build machine when available.
- `logs\server.log`: runtime log after starting the app.

## Offline deployment

1. Copy this whole folder to the offline computer.
2. Double-click `install_offline.bat`.
3. Double-click `start_event_intelligent.bat`.
4. Open `http://127.0.0.1:8001` if the browser does not open automatically.

Default account, when created by the backend: `admin / 123456`.
