# -*- coding: utf-8 -*-
from .core.occ_fallback import install_occ_fallback, USING_OCC_FALLBACK

install_occ_fallback()

from .core import OccSession, OccBody
from .runner import run_script_in_sandbox, inject_mock_environment

__version__ = "2.0.0"
OCC_AVAILABLE = True

__all__ = [
    "OccSession",
    "OccBody",
    "run_script_in_sandbox",
    "inject_mock_environment",
    "install_occ_fallback",
    "USING_OCC_FALLBACK",
    "OCC_AVAILABLE",
]
