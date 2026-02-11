# modules/__init__.py

from .dashboard import DashboardModule
from .system_status import SystemStatusModule
from .log.log import LogModule
from .git_manager import GitManagerModule

# Re-export widgets from system_status
from .system_status import CPUWidget, MemoryWidget, DiskWidget

# Optional: make __all__ for clarity
__all__ = [
    "DashboardModule",
    "SystemStatusModule",
    "CPUWidget",
    "MemoryWidget",
    "DiskWidget",
    "LogModule",
    "GitManagerModule",
]
