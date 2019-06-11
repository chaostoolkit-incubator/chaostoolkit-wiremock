# -*- coding: utf-8 -*-
from logzero import logger

from chaoslib.types import Configuration
from sky_wiremock.sky_wiremock import Wiremock
from .utils import get_wm_params, check_configuration

__all__ = [
        "add_mappings",
        "populate_from_dir",
        "delete_mappings",
        "global_fixed_delay",
        "global_random_delay",
        "fixed_delay"
        "random_delay",
        "chunked_dribble_delay",
        "down",
        "up",
        "reset"
]


def add_mappings(mappings: list=[], configuration: Configuration={}):
    """ adds more mappings to wiremock
    returns the list of ids of the mappings added
    """
    if (not check_configuration(configuration)):
        return []

    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])
    return w.populate(mappings)


def populate_from_dir(dir: str=".", configuration: Configuration={}):
    """ adds all mappings found in the passed folder
    returns the list of ids of the mappings added
    """
    if (not check_configuration(configuration)):
        return []

    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])
    return w.populate_from_dir(dir)


def delete_mappings(filters: list=[], configuration: Configuration={}):
    """ deletes a list of mappings
    returns the list of ids of the mappings deleted
    """
    if (not check_configuration(configuration)):
        return []

    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    ids = []
    for filter in filters:
        mapping = w.mapping_by_request(filter)
        if ("id" not in mapping):
            logger.error("Error: mapping {} {} not found".format(method, url))
            continue
        ids.append(w.delete_mapping(mapping["id"]))
    return ids


def down(filter: list=[], configuration: Configuration={}):
    """ set a list of services down
    more correctly it adds a chunked dribble delay to the mapping
    as defined in the configuration section (or action attributes)
    Returns the list of delayed mappings
    """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    conf = configuration.get('wiremock', {})
    if ('defaults' not in conf):
        logger.error("down defaults not specified in config")
        return -1

    defaults = conf.get('defaults',{})
    if ('down' not in defaults):
        logger.error("down defaults not specified in config")
        return -1

    delayed = []
    for f in filter:
        delayed.append(w.chunked_dribble_delay(f, defaults['down']))
    return delayed


def global_fixed_delay(fixedDelay: int=0, configuration: Configuration={}):
    """ add a fixed delay to all mappings """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])
    return w.global_fixed_delay(fixedDelay)


def global_random_delay(delayDistribution: dict={}, configuration: Configuration={}):
    """ adds a random delay to all mappings """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])
    return w.global_random_delay(delayDistribution)

    
def fixed_delay(filter: list, fixedDelayMilliseconds: int, configuration: Configuration={}):
    """ adds a fixed delay to a list of mappings """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    updated=[]
    for f in filter:
        updated.append(w.fixed_delay(f, fixedDelayMilliseconds))
    return updated


def random_delay(filter: list=[], delayDistribution: dict={}, configuration: Configuration={}):
    """adds a random delay to a list of mapppings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    updated=[]
    for f in filter:
        updated.append(w.random_delay(f, delayDistribution))
    return updated


def chunked_dribble_delay(filter: list=[], chunkedDribbleDelay: dict={}, configuration: Configuration={}):
    """adds a chunked dribble delay to a list of mappings"""
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    updated=[]
    for f in filter:
        updated.append(w.chunked_dribble_delay(f, chunkedDribbleDelay))
    return updated


def up(filter: list=[], configuration: Configuration={}):
    """ deletes all delays connected with a list of mappings """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    return w.up(filter)

def reset(configuration: Configuration={}):
    """ resets the wiremock server: deletes all mappings! """
    params = get_wm_params(configuration)
    w = Wiremock(url=params['url'], timeout=params['timeout'])

    return w.reset()
