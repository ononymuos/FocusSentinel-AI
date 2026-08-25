"""
FocusSentinel AI - Intelligent Vision & Attention Monitoring Engine
"""

__version__ = "1.1.0"
__author__ = "Usama Baig"
__copyright__ = "Copyright (c) 2026 Usama Baig. All rights reserved."
__license__ = "MIT"

from .config import SentinelConfig
from .engine import FocusSentinelEngine
from .core.state import FocusState, SessionMetrics

__all__ = [
    "SentinelConfig",
    "FocusSentinelEngine",
    "FocusState",
    "SessionMetrics",
]
