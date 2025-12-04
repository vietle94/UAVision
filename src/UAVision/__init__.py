# ...existing code...
"""
UAVision package init — lazy submodule loading and version fallback.
"""
from __future__ import annotations

import importlib
import importlib.metadata as _metadata
from typing import Any

# package version (fall back to static when not installed)
try:
    __version__ = _metadata.version("UAVision")
except _metadata.PackageNotFoundError:
    __version__ = "1.0.0"

# submodules provided by this package; they will be imported lazily
_SUBMODULES = {
    "mavic",
    "bme",
    "cpc",
    "mcda",
    "pops"
}

__all__ = list(_SUBMODULES) + ["__version__"]


def __getattr__(name: str) -> Any:
    """
    Lazily import and expose submodules as attributes on the package.

    Example:
        from UAVision import mcda  # imports UAVision.mcda on demand
    """
    if name in _SUBMODULES:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module  # cache on the package module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    # include lazy submodules in attribute listings (help(), tab-completion)
    return sorted(list(globals().keys()) + list(_SUBMODULES))