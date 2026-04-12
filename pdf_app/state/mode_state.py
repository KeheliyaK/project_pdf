from __future__ import annotations

from enum import Enum


class AppMode(str, Enum):
    HOME = "home"
    VIEWER = "viewer"
    EDITOR = "editor"
