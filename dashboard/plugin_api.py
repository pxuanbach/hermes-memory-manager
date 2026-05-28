"""Memory Manager dashboard plugin — backend API routes.

Mounted at /api/plugins/memory-manager/ by the dashboard plugin system.
Serves and edits:
  - Default: ~/.hermes/memories/MEMORY.md and USER.md
  - Per-profile: ~/.hermes/profiles/<profile>/memories/MEMORY.md and USER.md
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query
except Exception:
    def Query(*_args, **_kwargs):
        return None

    class APIRouter:
        def get(self, *_args, **_kwargs):
            return lambda fn: fn
        def put(self, *_args, **_kwargs):
            return lambda fn: fn

    class HTTPException(Exception):
        def __init__(self, status_code=400, detail=""):
            self.status_code = status_code
            self.detail = detail

try:
    from hermes_constants import get_hermes_home
except Exception:
    import os as _os

    def get_hermes_home() -> Path:
        val = (_os.environ.get("HERMES_HOME") or "").strip()
        return Path(val) if val else Path.home() / ".hermes"

log = logging.getLogger(__name__)
router = APIRouter()

MEMORY_FILES = ["MEMORY.md", "USER.md"]


def _memory_dir(profile: str | None = None) -> Path:
    """Return memories directory for a profile, or the default memories directory."""
    home = get_hermes_home()
    if profile:
        return home / "profiles" / profile / "memories"
    return home / "memories"


def _memory_path(name: str, profile: str | None = None) -> Path:
    """Return Path for a memory file. Accepts 'MEMORY', 'MEMORY.md', 'USER', 'USER.md'."""
    name = name.replace(".md", "")  # strip any existing .md
    return _memory_dir(profile) / f"{name}.md"


@router.get("/profiles")
async def list_profiles() -> dict[str, Any]:
    """List available profiles (including 'default')."""
    home = get_hermes_home()
    profiles_dir = home / "profiles"
    profiles = ["default"]

    if profiles_dir.is_dir():
        for item in profiles_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                profiles.append(item.name)

    profiles.sort()
    return {"profiles": profiles}


@router.get("/files")
async def list_memory_files(profile: str | None = Query(default=None)) -> dict[str, Any]:
    """List available memory files (MEMORY.md, USER.md) for the given profile."""
    mem_dir = _memory_dir(profile)
    files = []
    for name in MEMORY_FILES:
        p = _memory_path(name, profile)
        files.append({
            "name": name,
            "path": str(p),
            "exists": p.exists(),
            "size": p.stat().st_size if p.exists() else 0,
        })
    return {"files": files, "profile": profile or "default"}


@router.get("/files/{name}")
async def read_memory_file(name: str, profile: str | None = Query(default=None)) -> dict[str, Any]:
    """Read the content of a memory file for the given profile.

    If the file does not exist, returns empty content (status 200) so the UI
    can present a blank textarea for the user to fill in and save.
    """
    if not name.endswith(".md"):
        name = f"{name}.md"
    p = _memory_path(name, profile)
    if not p.exists():
        # Return empty content — user can write it via the save endpoint
        return {"name": name, "content": "", "size": 0, "profile": profile or "default"}
    try:
        content = p.read_text(encoding="utf-8")
        return {"name": name, "content": content, "size": len(content), "profile": profile or "default"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/files/{name}")
async def write_memory_file(name: str, body: dict[str, str], profile: str | None = Query(default=None)) -> dict[str, Any]:
    """Write content to a memory file for the given profile. Creates the file if it doesn't exist."""
    if not name.endswith(".md"):
        name = f"{name}.md"
    p = _memory_path(name, profile)

    # Security: ensure path stays within memories dir
    try:
        resolved = p.resolve()
        mem_dir = _memory_dir(profile).resolve()
        if not str(resolved).startswith(str(mem_dir)):
            raise HTTPException(status_code=400, detail="Path traversal blocked")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    content = body.get("content", "")
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"success": True, "name": name, "size": len(content), "profile": profile or "default"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))