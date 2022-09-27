# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Mapping

from chaoslib.types import Configuration
from logzero import logger

from .driver import Wiremock
from .utils import check_configuration, get_wm_params

__all__ = [
    "add_mappings",
    "populate_from_dir",
    "update_mappings_status_code_and_body",
    "update_mappings_fault",
    "delete_mappings",
    "delete_all_mappings",
    "global_fixed_delay",
    "global_random_delay",
    "fixed_delay",
    "random_delay",
    "chunked_dribble_delay",
    "down",
    "up",
    "reset",
    "reset_mappings",
]


def add_mappings(
    mappings: List[Any], configuration: Configuration = None
) -> List[Any]:
    """adds more mappings to wiremock
    returns the list of ids of the mappings added
    """
    if not check_configuration(configuration):
        return []

    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])
    return w.populate(mappings)


def populate_from_dir(
    dir: str = ".", configuration: Configuration = None
) -> List[Any]:
    """adds all mappings found in the passed folder
    returns the list of ids of the mappings added
    """
    if not check_configuration(configuration):
        return []

    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])
    return w.populate_from_dir(dir)


def delete_mappings(
    filter: List[Any],
    filter_opts: Dict[str, Any] = None,
    configuration: Configuration = None,
) -> List[Any]:
    """deletes a list of mappings
    returns the list of ids of the mappings deleted
    """
    if not check_configuration(configuration):
        return []

    filter_opts = filter_opts or {}

    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    ids = []
    for f in filter:
        mappings = w.filter_mappings(f, **filter_opts)
        if not mappings:
            logger.error("No mapping match found for filter %s", f)
            continue

        for mapping in mappings:
            ids.append(w.delete_mapping(mapping["id"]))
    return ids


def delete_all_mappings(configuration: Configuration = None) -> bool:
    """deletes all mappings
    returns true if delete was successful and false if not
    """
    if not check_configuration(configuration):
        return False

    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])
    return w.delete_all_mappings()


def update_mappings_status_code_and_body(
    filter: List[Mapping],
    status_code: str,
    body: str = None,
    body_file_name: str = None,
    filter_opts: Dict[str, Any] = None,
    configuration: Configuration = None,
) -> List[Any]:
    """changes all Wiremock mappings responses to the set status_code and body.
    :param filter: the mappings filter
    :param status_code: the new http status code
    :param body: (optional) the response body as a string
    :param body_file_name: (optional) the response body as a file
    returns the list of ids of the mappings changed
    """
    if not check_configuration(configuration):
        return []

    if not status_code:
        return []

    filter_opts = filter_opts or {}

    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    mappings_to_update: List[Mapping] = []
    for f in filter:
        mappings_to_update.extend(w.filter_mappings(f, **filter_opts))

    if len(mappings_to_update) > 0:
        return w.update_status_code_and_body(
            mappings_to_update,
            status_code=status_code,
            body=body,
            body_file_name=body_file_name,
        )

    return []


def update_mappings_fault(
    filter: List[Mapping],
    fault: str,
    filter_opts: Dict[str, Any] = None,
    configuration: Configuration = None,
) -> List[Any]:
    """updates wiremock fault configuration for selected mappings.
    :param filter: the mappings filter
    :param filter_limit: limit the number of mappings the filter \
can match. Use `0` for all mappings
    :param filter_strict: use strict match with mappings filter. \
Default is True
    :param fault: the Wiremock fault to apply to selected mappings
    :return: a list of updated mappings
    """
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    filter_opts = filter_opts or {}

    mappings_to_update: List[Any] = []
    for f in filter:
        mappings = w.filter_mappings(f, **filter_opts)
        if mappings:
            mappings_to_update.extend(mappings)
        else:
            logger.error("No mappings found")

    if len(mappings_to_update) > 0:
        return w.update_fault(mappings_to_update, fault)

    return []


def down(
    filter: List[Mapping], configuration: Configuration = None
) -> List[Any]:
    """set a list of services down
    more correctly it adds a chunked dribble delay to the mapping
    as defined in the configuration section (or action attributes)
    Returns the list of delayed mappings
    """
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    conf = configuration.get("wiremock", {})
    if "defaults" not in conf:
        logger.error("Down defaults not specified in config")
        return []

    defaults = conf.get("defaults", {})
    if "down" not in defaults:
        logger.error("Down defaults not specified in config")
        return []

    delayed = []
    for f in filter:
        delayed.append(w.chunked_dribble_delay(f, defaults["down"]))

    return delayed


def global_fixed_delay(
    fixedDelay: int = 0, configuration: Configuration = None
) -> int:
    """add a fixed delay to all mappings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])
    return w.global_fixed_delay(fixedDelay)


def global_random_delay(
    delayDistribution: Mapping[str, Any], configuration: Configuration = None
) -> int:
    """adds a random delay to all mappings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])
    return w.global_random_delay(delayDistribution)


def fixed_delay(
    filter: List[Any],
    fixedDelayMilliseconds: int,
    filter_opts: Dict[str, Any] = None,
    configuration: Configuration = None,
) -> List[Any]:
    """adds a fixed delay to a list of mappings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    filter_opts = filter_opts or {}

    mappings_to_update: List[Any] = []
    for f in filter:
        mappings = w.filter_mappings(f, **filter_opts)
        if mappings:
            mappings_to_update.extend(mappings)
        else:
            logger.error("No mappings found")

    if len(mappings_to_update) > 0:
        return w.fixed_delay(mappings_to_update, fixedDelayMilliseconds)

    return []


def random_delay(
    filter: List[Any],
    delayDistribution: Mapping[str, Any],
    configuration: Configuration = None,
) -> List[Any]:
    """adds a random delay to a list of mapppings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    updated = []
    for f in filter:
        updated.append(w.random_delay(f, delayDistribution))

    return updated


def chunked_dribble_delay(
    filter: List[Any],
    chunkedDribbleDelay: Mapping[str, Any],
    configuration: Configuration = None,
) -> List[Any]:
    """adds a chunked dribble delay to a list of mappings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    updated = []
    for f in filter:
        updated.append(w.chunked_dribble_delay(f, chunkedDribbleDelay))

    return updated


def up(filter: List[Any], configuration: Configuration = None) -> List[Any]:
    """deletes all delays connected with a list of mappings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    return w.up(filter)


def reset(configuration: Configuration = None) -> int:
    """resets the wiremock server: deletes all mappings!"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    return w.reset()


def reset_mappings(configuration: Configuration = None) -> int:
    """resets the wiremock server: deletes all in-memory mappings!"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params["url"], timeout=params["timeout"])

    return w.reset_mappings()
