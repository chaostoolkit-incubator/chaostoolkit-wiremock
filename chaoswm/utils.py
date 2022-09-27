# -*- coding: utf-8 -*-
import socket
from contextlib import closing
from typing import Any, Dict, Optional

from logzero import logger

__all__ = ["can_connect_to", "get_wm_params", "check_configuration"]


def can_connect_to(host: str, port: int) -> bool:
    """Test a connection to a host/port"""

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return bool(sock.connect_ex((host, port)) == 0)


def get_wm_params(configuration: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Calculate wiremock parameters"""
    wm_conf = configuration.get("wiremock", {})

    host = wm_conf.get("host", None)
    port = wm_conf.get("port", None)
    context_path = wm_conf.get("contextPath", "")
    timeout = wm_conf.get("timeout", 1)

    url = ""

    if host and port:
        url = f"http://{host}:{port}{context_path}"
    else:
        url = wm_conf.get("url", None)

    if not url:
        logger.error("No configuration params to set WM server url")
        return None

    return {"url": url, "timeout": timeout}


def check_configuration(configuration: Dict[str, Any] = None) -> bool:
    """Check configuration contains valid wiremock settings"""
    configuration = configuration or {}
    if "wiremock" not in configuration:
        logger.error("Error: wiremock key not found in configuration section")
        return False
    return True
