"""Shared helpers used by Splash and its mixins.

Kept tiny on purpose — anything importable by both the main window and the
mixins lives here to avoid circular imports.
"""

import os
import stat


def make_executable(path):
    """Cross-platform `chmod +x`. No-op on Windows (no concept of an exec bit)."""
    if os.name == 'nt':
        return
    try:
        current = os.stat(path).st_mode
        os.chmod(path, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError as e:
        print(f"Warning: could not chmod +x {path}: {e}")
