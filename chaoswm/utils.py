from contextlib import closing
import socket
from typing import Any, Dict, Optional

from logzero import logger

__all__ = ["can_connect_to", "get_wm_params", "check_configuration"]


def can_connect_to(host: str, port: int) -> bool:
    """ Test a connection to a host/port """

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return bool(sock.connect_ex((host, port)) == 0)


def get_wm_params(c: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    wm_conf = c.get("wiremock", {})

    host = wm_conf.get("host", None)
    port = wm_conf.get("port", None)
    url = wm_conf.get("url", None)
    context_path = wm_conf.get("contextPath", "")
    timeout = wm_conf.get("timeout", 1)

    if host and port:
        url = "http://{}:{}{}".format(host, port, context_path)

    if not url:
        logger.error("No configuration params to set WM server url")
        return None

    return {"url": url, "timeout": timeout}


def check_configuration(c: Dict[str, Any] = None) -> bool:
    c = c or {}
    if "wiremock" not in c:
        logger.error("Error: wiremock key not found in configuration section")
        return False
    return True
