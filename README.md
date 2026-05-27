# Hermes Memory Manager

A Hermes dashboard plugin for viewing and editing persistent memory files — MEMORY.md and USER.md.

## Features

- **MEMORY tab**: View and edit `~/.hermes/memories/MEMORY.md`
- **USER tab**: View and edit `~/.hermes/memories/USER.md`
- Editable textarea with Save button to persist changes to disk
- Success and error feedback messages

## Plugin Description

Memory Manager provides a UI for managing Hermes persistent memory. It connects to a Python backend API (`/api/plugins/memory-manager/`) that handles file I/O operations against `~/.hermes/memories/`. The plugin runs as a tab inside the Hermes dashboard at `http://127.0.0.1:9119`.

## How to Integrate with Hermes Dashboard

The plugin is auto-discovered by the Hermes dashboard when placed in `~/.hermes/plugins/memory-manager/`.

**Requirements:**
- Dashboard plugin manifest: `dashboard/manifest.json`
- Web UI bundle: `dashboard/dist/index.js`
- Backend API handler: `dashboard/plugin_api.py`
- Plugin registered in Hermes config (`plugins.memory-manager` enabled)

**File structure:**
```
memory-manager/
├── dashboard/
│   ├── dist/
│   │   └── index.js       # Built UI bundle
│   ├── plugin_api.py      # Backend API endpoints
│   └── manifest.json      # Plugin manifest
├── README.md
```

**Installation:**
1. Copy plugin to `~/.hermes/plugins/memory-manager/`
2. Enable in `~/.hermes/config.yaml`:
   ```yaml
   plugins:
     memory-manager:
       enabled: true
   ```
3. Restart Hermes dashboard
4. The "Memory Manager" tab appears automatically in the dashboard sidebar

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/plugins/memory-manager/files` | List memory files |
| GET | `/api/plugins/memory-manager/files/{name}` | Read memory file content |
| PUT | `/api/plugins/memory-manager/files/{name}` | Write memory file content |