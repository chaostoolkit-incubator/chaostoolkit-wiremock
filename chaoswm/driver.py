# -*- coding: utf-8 -*-
"""

This module implements a few functions to handle mappings on a wiremock server.
It is meant not to be complete and to be the most transparent possible,
in contrast with the official wiremock driver. For example there is no
validation of the payloads.

"""

import glob
import json
import os
from typing import Any, Dict, List, Mapping

import requests
from logzero import logger

from .utils import can_connect_to


class ConnectionError(Exception):
    pass


class Wiremock(object):

    def __init__(
            self,
            host: str = None,
            port: str = None,
            url: str = None,
            timeout: int = 1):

        if (host and port):
            url = "http://{}:{}".format(host, port)
        self.base_url = "{}/__admin".format(url)
        self.mappings_url = "{}/{}".format(self.base_url, "mappings")
        self.settings_url = "{}/{}".format(self.base_url, "settings")
        self.reset_url = "{}/{}".format(self.base_url, "reset")
        self.timeout = timeout
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        if (host and port) and can_connect_to(host, port) is False:
            raise ConnectionError("Wiremock server not found")

    def mappings(self) -> List[Any]:
        """
        retrieves all mappings
        returns the array of mappings found
        """
        r = requests.get(
            self.mappings_url,
            headers=self.headers,
            timeout=self.timeout)
        if r.status_code != 200:
            logger.error(
                "[mappings]:Error retrieving mappings: {}".format(
                    r.text()))
            return []
        else:
            res = r.json()
            return res["mappings"]

    def mapping_by_id(self, id=int) -> Dict[str, Any]:
        r = requests.get(
            "{}/{}".format(self.mappings_url, id),
            headers=self.headers,
            timeout=self.timeout)
        if r.status_code != 200:
            logger.error(
                "[mapping_by_id]:Error retrieving mapping: {}".format(
                    r.text()))
            return -1
        else:
            return r.json()

    def mapping_by_url_and_method(
            self, url: str, method: str) -> Dict[str, Any]:
        mappings = self.mappings()
        for mapping in mappings:
            if ((mapping["request"]["url"] == url) and
                    (mapping["request"]["method"] == method)):
                return mapping
        return {}

    def mapping_by_request(
            self, request: Mapping[str, Any] = None) -> Dict[str, Any]:
        num_filter_keys = len(request.keys())
        mappings = self.mappings()
        for mapping in mappings:
            count = 0
            inter = mapping['request'].keys() & request.keys()
            if len(inter) != num_filter_keys:
                continue
            for k in request.keys():
                if mapping['request'][k] == request[k]:
                    count += 1
            if count == num_filter_keys:
                return mapping
        return None

    def mapping_by_request_exact_match(
            self, request: Mapping[str, Any] = None) -> Dict[str, Any]:
        mappings = self.mappings()
        for mapping in mappings:
            if mapping['request'] == request:
                return mapping
        return None

    def populate(self, mappings: Mapping[str, Any]) -> List[Any]:
        """ Populate: adds all passed mappings
            Returns the list of ids of mappings created
        """
        if isinstance(mappings, list) is False:
            logger.error("[populate]:ERROR: mappings should be a list")
            return None

        ids = []
        for mapping in mappings:
            id = self.add_mapping(mapping)
            if id is not None:
                ids.append(id)
            else:
                logger.error("[populate]:ERROR adding a mapping")
                return None

        return ids

    def populate_from_dir(self, dir: str) -> List[Any]:
        """ reads all json files in a directory and adds all mappings
            Returns the list of ids of mappings created
            or None in case of errors
        """
        if not os.path.exists(dir):
            logger.error(
                "[populate_from_dir]: directory {} does not exists".format(dir))
            return None

        ids = []
        for filename in glob.glob(os.path.join(dir, '*.json')):
            logger.info("Importing {}".format(filename))
            with open(filename) as f:
                mapping = json.load(f)
                id = self.add_mapping(mapping)
                if id is not None:
                    ids.append(id)
        return ids

    def update_mapping(self,
                       id: str = "",
                       mapping: Mapping[str,
                                        Any] = None) -> Dict[str,
                                                             Any]:
        """ updates the mapping pointed by id with new mapping """
        r = requests.put(
            "{}/{}".format(self.mappings_url, id),
            headers=self.headers,
            data=json.dumps(mapping),
            timeout=self.timeout)
        if r.status_code != 200:
            logger.error("Error updating a mapping: " + r.text)
            return None
        else:
            return r.json()

    def add_mapping(self, mapping: Mapping[str, Any]) -> int:
        """ add_mapping: add a mapping passed as attribute """
        r = requests.post(
            self.mappings_url,
            headers=self.headers,
            data=json.dumps(mapping),
            timeout=self.timeout)
        if r.status_code != 201:
            logger.error("Error creating a mapping: " + r.text)
            return None
        else:
            res = r.json()
            return res['id']

    def delete_mapping(self, id: str):
        r = requests.delete(
            "{}/{}".format(self.mappings_url, id),
            timeout=self.timeout)
        if r.status_code != 200:
            logger.error("Error deleting mapping {}: {}".format(id, r.text))
            return -1
        else:
            return id

    def delete_all_mappings(self):
        mappings = self.mappings()
        for mapping in mappings:
            self.delete_mapping(mapping["id"])
        return len(mappings)

    def fixed_delay(
            self,
            request: Dict = None,
            fixedDelayMilliseconds: int = 0) -> Dict:
        """
        updates the mapping adding a fixed delay
        returns the updated mapping or none in case of errors
        """
        mapping_found = self.mapping_by_request_exact_match(request)

        if not mapping_found:
            logger.error("[fixed_delay]: Error retrieving mapping")
            return None

        mapping_found["response"]["fixedDelayMilliseconds"] = fixedDelayMilliseconds
        return self.update_mapping(mapping_found["id"], mapping_found)

    def global_fixed_delay(self, fixedDelay: int) -> int:
        r = requests.post(
            self.settings_url,
            headers=self.headers,
            data=json.dumps({"fixedDelay": fixedDelay}),
            timeout=self.timeout)
        if r.status_code != 200:
            logger.error(
                "[global_fixed_delay]: Error setting delay: {}".format(
                    r.text))
            return -1
        else:
            return 1

    def random_delay(self,
                     filter: Mapping[str,
                                     Any],
                     delayDistribution: Mapping[str,
                                                Any]) -> Dict[str,
                                                              Any]:
        """
        Updates the mapping adding a random delay
        returns the updated mapping or none in case of errors
        """
        if not isinstance(delayDistribution, dict):
            logger.error("[random_delay]: parameter has to be a dictionary")

        mapping_found = self.mapping_by_request_exact_match(filter)

        if not mapping_found:
            logger.error("[random_delay]: Error retrieving mapping")
            return None

        mapping_found["response"]["delayDistribution"] = delayDistribution
        return self.update_mapping(mapping_found["id"], mapping_found)

    def global_random_delay(self, delayDistribution: Mapping[str, Any]) -> int:
        if not isinstance(delayDistribution, dict):
            logger.error(
                "[global_random_delay]: parameter has to be a dictionary")
        r = requests.post(
            self.settings_url,
            headers=self.headers,
            data=json.dumps({"delayDistribution": delayDistribution}),
            timeout=self.timeout)
        if r.status_code != 200:
            logger.error(
                "[global_random_delay]: Error setting delay: {}".format(
                    r.text))
            return -1
        else:
            return 1

    def chunked_dribble_delay(self,
                              filter: List[Any],
                              chunkedDribbleDelay: Mapping[str,
                                                           Any] = None):
        """
        Adds a delay to the passed mapping
        returns the updated mapping or non in case of errors
        """
        if not isinstance(chunkedDribbleDelay, dict):
            logger.error(
                "[chunked_dribble_delay]: parameter has to be a dictionary")
        if "numberOfChunks" not in chunkedDribbleDelay:
            logger.error(
                "[chunked_dribble_delay]: attribute numberOfChunks not found in parameter")
            return None
        if "totalDuration" not in chunkedDribbleDelay:
            logger.error(
                "[chunked_dribble_delay]: attribute totalDuration not found in parameter")
            return None

        mapping_found = self.mapping_by_request_exact_match(filter)

        if not mapping_found:
            logger.error("[chunked_dribble_delay]: Error retrieving mapping")
            return None

        mapping_found["response"]["chunkedDribbleDelay"] = chunkedDribbleDelay
        return self.update_mapping(mapping_found["id"], mapping_found)

    def up(self, filter: List[Any] = None) -> List[Any]:
        """ resets a list of mappings deleting all delays attached to them """
        ids = []
        for f in filter:
            mapping_found = self.mapping_by_request_exact_match(f)
            if not mapping_found:
                next
            else:
                logger.debug(
                    "[up]: found mapping: {}".format(
                        mapping_found["id"]))
                for key in [
                    'fixedDelayMilliseconds',
                    'delayDistribution',
                        'chunkedDribbleDelay']:
                    if key in mapping_found["response"]:
                        del mapping_found["response"][key]
                self.update_mapping(mapping_found["id"], mapping_found)
                ids.append(mapping_found["id"])
        return ids

    def reset(self) -> int:
        r = requests.post(
            self.reset_url,
            headers=self.headers,
            timeout=self.timeout)
        if r.status_code != 200:
            logger.error("[reset]:Error resetting wiremock server " + r.text)
            return -1
        else:
            return 1
