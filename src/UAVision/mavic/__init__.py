from __future__ import annotations

import importlib
from typing import Any

# submodules provided by this package; they will be imported lazily
_SUBMODULES = {
    "merge_sensor_data",
    "merge_wind_data",
    "preprocess",
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
