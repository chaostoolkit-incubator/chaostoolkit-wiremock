# -*- coding: utf-8 -*-
"""Top-level package for chaoswm."""
from typing import List
from logzero import logger

from chaoslib.discovery.discover import discover_actions, discover_probes, \
    initialize_discovery_result
from chaoslib.exceptions import DiscoveryFailed
from chaoslib.types import Discovery, DiscoveredActivities, \
    DiscoveredSystemInfo, Secrets

name = "chaoswm"
__author__ = """Marco Masetti"""
__email__ = 'grubert65@gmail.com'
__version__ = '0.1.5'
__all__ = ["discover", "__version__"]


def discover(discover_system: bool = True) -> Discovery:
    logger.info("Discovering capabilities from chaostoolkit-wiremock")

    discovery = initialize_discovery_result(
        "chaostoolkit-wiremock", __version__, "wiremock")
    discovery["activities"].extend(load_exported_activities())
    return discovery


###############################################################################
# Private functions
###############################################################################
def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract metadata from actions and probes exposed by this extension.
    """
    activities = []
    activities.extend(discover_actions("chaoswm.actions"))
    return activities
