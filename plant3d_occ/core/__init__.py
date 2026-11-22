# -*- coding: utf-8 -*-
from .occ_fallback import install_occ_fallback, USING_OCC_FALLBACK

install_occ_fallback()

from .body import OccBody
from .session import OccSession
from .math3d import mPoint, mVector, mTransform, asRadiants, asDegrees, areEqual, pi, mcPi

__all__ = [
    "OccBody",
    "OccSession",
    "mPoint",
    "mVector",
    "mTransform",
    "asRadiants",
    "asDegrees",
    "areEqual",
    "pi",
    "mcPi",
    "install_occ_fallback",
    "USING_OCC_FALLBACK",
]
