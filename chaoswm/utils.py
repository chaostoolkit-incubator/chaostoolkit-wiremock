import socket
from logzero import logger

from contextlib import closing


def can_connect_to(host, port):
    """ Test a connection to a host/port """

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return bool(sock.connect_ex((host, port)) == 0)


def get_wm_params(c: dict):
    wm_conf = c.get("wiremock", {})

    host = wm_conf.get("host", None)
    port = wm_conf.get("port", None)
    context_path = wm_conf.get("contextPath", "")
    timeout = wm_conf.get("timeout", 1)

    url = ""

    if host and port:
        url = "http://{}:{}{}".format(host, port, context_path)

    if not url:
        logger.error("ERROR: no configuration params to set WM server url")
        return None

    return {"url": url, "timeout": timeout}


def check_configuration(c: dict = {}):
    if "wiremock" not in c:
        logger.error("Error: wiremock key not found in configuration section")
        return -1
    return 1
