"""Memory Manager dashboard plugin — backend API routes.

Mounted at /api/plugins/memory-manager/ by the dashboard plugin system.
Serves and edits ~/.hermes/memories/MEMORY.md and USER.md.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

try:
    from fastapi import APIRouter, HTTPException
except Exception:
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

MEMORY_DIR = get_hermes_home() / "memories"
MEMORY_FILES = ["MEMORY.md", "USER.md"]


def _memory_path(name: str) -> Path:
    """Return Path for a memory file. Accepts 'MEMORY', 'MEMORY.md', 'USER', 'USER.md'."""
    name = name.replace(".md", "")  # strip any existing .md
    return MEMORY_DIR / f"{name}.md"


@router.get("/files")
async def list_memory_files() -> dict[str, Any]:
    """List available memory files (MEMORY.md, USER.md) with metadata."""
    files = []
    for name in MEMORY_FILES:
        p = _memory_path(name)
        files.append({
            "name": name,
            "path": str(p),
            "exists": p.exists(),
            "size": p.stat().st_size if p.exists() else 0,
        })
    return {"files": files}


@router.get("/files/{name}")
async def read_memory_file(name: str) -> dict[str, Any]:
    """Read the content of a memory file."""
    if not name.endswith(".md"):
        name = f"{name}.md"
    p = _memory_path(name)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {name}")
    try:
        content = p.read_text(encoding="utf-8")
        return {"name": name, "content": content, "size": len(content)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/files/{name}")
async def write_memory_file(name: str, body: dict[str, str]) -> dict[str, Any]:
    """Write content to a memory file. Creates the file if it doesn't exist."""
    if not name.endswith(".md"):
        name = f"{name}.md"
    p = _memory_path(name)
    # Security: ensure path stays within memories dir
    try:
        resolved = p.resolve()
        mem_dir = MEMORY_DIR.resolve()
        if not str(resolved).startswith(str(mem_dir)):
            raise HTTPException(status_code=400, detail="Path traversal blocked")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    content = body.get("content", "")
    try:
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"success": True, "name": name, "size": len(content)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))