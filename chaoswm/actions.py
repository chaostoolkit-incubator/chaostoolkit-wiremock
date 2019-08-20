# -*- coding: utf-8 -*-
from typing import Any, List, Mapping

from chaoslib.types import Configuration
from logzero import logger

from .driver import Wiremock
from .utils import check_configuration, get_wm_params

__all__ = [
    "add_mappings",
    "populate_from_dir",
    "delete_mappings",
    "global_fixed_delay",
    "global_random_delay",
    "fixed_delay",
    "random_delay",
    "chunked_dribble_delay",
    "down",
    "up",
    "reset"
]


def add_mappings(
        mappings: List[Any],
        configuration: Configuration = None) -> List[Any]:
    """ adds more mappings to wiremock
    returns the list of ids of the mappings added
    """
    if not check_configuration(configuration):
        return []

    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])
    return w.populate(mappings)


def populate_from_dir(
        dir: str = ".",
        configuration: Configuration = {}) -> List[Any]:
    """ adds all mappings found in the passed folder
    returns the list of ids of the mappings added
    """
    if not check_configuration(configuration):
        return []

    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])
    return w.populate_from_dir(dir)


def delete_mappings(
        filter: List[Any],
        configuration: Configuration = None) -> List[Any]:
    """ deletes a list of mappings
    returns the list of ids of the mappings deleted
    """
    if not check_configuration(configuration):
        return []

    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    ids = []
    for f in filter:
        mapping = w.mapping_by_request(f)
        if mapping is None:
            logger.error("Mapping {} {} not found".format(
                mapping["request"]["method"],
                mapping["request"]["url"]))
            continue
        ids.append(w.delete_mapping(mapping["id"]))
    return ids


def down(filter: List[Any], configuration: Configuration = None) -> List[Any]:
    """ set a list of services down
    more correctly it adds a chunked dribble delay to the mapping
    as defined in the configuration section (or action attributes)
    Returns the list of delayed mappings
    """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    conf = configuration.get('wiremock', {})
    if 'defaults' not in conf:
        logger.error("Down defaults not specified in config")
        return []

    defaults = conf.get('defaults', {})
    if 'down' not in defaults:
        logger.error("Down defaults not specified in config")
        return []

    delayed = []
    for f in filter:
        delayed.append(w.chunked_dribble_delay(f, defaults['down']))
    return delayed


def global_fixed_delay(
        fixedDelay: int = 0,
        configuration: Configuration = None) -> int:
    """ add a fixed delay to all mappings """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])
    return w.global_fixed_delay(fixedDelay)


def global_random_delay(
        delayDistribution: Mapping[str, Any],
        configuration: Configuration = None) -> int:
    """ adds a random delay to all mappings """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])
    return w.global_random_delay(delayDistribution)


def fixed_delay(
        filter: List[Any],
        fixedDelayMilliseconds: int,
        configuration: Configuration = None) -> List[Any]:
    """ adds a fixed delay to a list of mappings """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    updated = []
    for f in filter:
        updated.append(w.fixed_delay(f, fixedDelayMilliseconds))
    return updated


def random_delay(
        filter: List[Any],
        delayDistribution: Mapping[str, Any],
        configuration: Configuration = None) -> List[Any]:
    """adds a random delay to a list of mapppings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    updated = []
    for f in filter:
        updated.append(w.random_delay(f, delayDistribution))
    return updated


def chunked_dribble_delay(
        filter: List[Any],
        chunkedDribbleDelay: Mapping[str, Any],
        configuration: Configuration = None) -> List[Any]:
    """adds a chunked dribble delay to a list of mappings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    updated = []
    for f in filter:
        updated.append(w.chunked_dribble_delay(f, chunkedDribbleDelay))
    return updated


def up(filter: List[Any], configuration: Configuration = None) -> List[Any]:
    """ deletes all delays connected with a list of mappings """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    return w.up(filter)


def reset(configuration: Configuration = None) -> int:
    """ resets the wiremock server: deletes all mappings! """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    return w.reset()
