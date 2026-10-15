"""
frames/__init__.py
──────────────────
Makes the frames/ directory a Python package.

Re-exports every frame class so app.py can do a single clean import:

    from frames import DashboardFrame, LibraryFrame, AssetFrame,
                       MembersFrame, SettingsFrame
"""

from frames.dashboard import DashboardFrame
from frames.library   import LibraryFrame
from frames.assets    import AssetFrame
from frames.members   import MembersFrame
from frames.settings  import SettingsFrame

__all__ = [
    'DashboardFrame',
    'LibraryFrame',
    'AssetFrame',
    'MembersFrame',
    'SettingsFrame',
]