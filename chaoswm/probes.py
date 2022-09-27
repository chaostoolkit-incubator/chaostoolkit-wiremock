# -*- coding: utf-8 -*-
from chaoslib.types import Configuration
from logzero import logger
from typing import Any, List

from .driver import ConnectionError, Wiremock
from .utils import check_configuration, get_wm_params

__all__ = ["mappings", "server_running"]


def server_running(configuration: Configuration = None) -> int:
    if not check_configuration(configuration):
        logger.error("Configuration error")
        return None

    params = get_wm_params(configuration)
    try:
        Wiremock(url=params["url"], timeout=params["timeout"])
        return 1
    except ConnectionError:
        logger.error("Wiremock server not running")
        return 0


def mappings(configuration: Configuration = None) -> List[Any]:
    if not check_configuration(configuration):
        return []
    try:
        params = get_wm_params(configuration)
        w = Wiremock(url=params["url"], timeout=params["timeout"])
        return w.mappings()
    except ConnectionError:
        logger.error("Error connecting to Wiremock server")
        return None
