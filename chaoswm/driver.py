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
from typing import Any, Dict, List, Mapping, Optional

from logzero import logger
import requests

from .utils import can_connect_to

AVAILABLE_FAULTS = [
    "EMPTY_RESPONSE",
    "MALFORMED_RESPONSE_CHUNK",
    "RANDOM_DATA_THEN_CLOSE",
    "CONNECTION_RESET_BY_PEER",
]


class ConnectionError(Exception):
    """represents a connection error when connecting to wiremock"""


class Wiremock:
    """driver class to interface with the wiremock admin API"""

    def __init__(
        self,
        host: str = None,
        port: str = None,
        url: str = None,
        timeout: int = 1,
    ):

        if host and port:
            url = f"http://{host}:{port}"
        self.base_url = f"{url}/__admin"
        self.mappings_url = f"{self.base_url}/mappings"
        self.settings_url = f"{self.base_url}/settings"
        self.reset_url = f"{self.base_url}/reset"
        self.reset_mappings_url = f"{self.mappings_url}/reset"
        self.timeout = timeout
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if (host and port) and can_connect_to(host, port) is False:
            raise ConnectionError("Wiremock server not found")

    def mappings(self) -> List[Any]:
        """
        retrieves all mappings
        returns the array of mappings found
        """
        response = requests.get(
            self.mappings_url, headers=self.headers, timeout=self.timeout
        )
        if response.status_code != 200:
            logger.error(
                "[mappings]:Error retrieving mappings: %s", response.text
            )
            return []

        res = response.json()
        return res["mappings"]

    def mapping_by_id(self, stub_id=int) -> Dict[str, Any]:
        """retrieve the stub mapping configuration from wiremock with
        with the given id"""
        response = requests.get(
            f"{self.mappings_url}/{stub_id}",
            headers=self.headers,
            timeout=self.timeout,
        )
        if response.status_code != 200:
            logger.error(
                "[mapping_by_id]:Error retrieving mapping: %s", response.text
            )
            return -1

        return response.json()

    def filter_mapping(self, _filter: Mapping, strict: bool = True) -> Mapping:
        """search for matching stub mappings in wiremock
        Returns the first matching stub mapping"""
        matching_mappings = self.filter_mappings(_filter, strict, limit=1)
        return matching_mappings[1] if len(matching_mappings) > 0 else None

    def filter_mappings(
        self, _filter: Mapping, strict: bool = True, limit: int = 0
    ) -> List[Mapping]:
        """search for matching stub mappings in wiremock
        Returns a list of matchimg mappings"""
        mappings = self.mappings()

        matching_mappings = []
        count = 0
        for mapping in mappings:
            if strict:
                node = mapping.get("request")
                matches = self.strict_filter(node, _filter)
            else:
                matches = self.recursive_filter(mapping, _filter)

            if matches:
                matching_mappings.append(mapping)
                count += 1

            if 0 < limit <= count:
                break

        return matching_mappings

    def strict_filter(self, node: Mapping, _filter: Mapping) -> bool:
        """(legacy) match mappings metadata with builtin equality comparison
        Returns True if mapping matches the filter, False otherwise."""
        intersec = node.keys() & _filter.keys()
        if len(intersec) != len(_filter.keys()):
            return False
        for key in _filter.keys():
            filter_value = _filter[key]
            comp = node.get(key)
            if filter_value != comp:
                return False
        return True

    def recursive_filter(
        self, node: Mapping, _filter: Mapping, depth: int = 0
    ) -> bool:
        """match mappings metadata by recursively comparing node by node
        with the stub mapping.
        Returns True if mapping matches the filter, False otherwise."""
        intersec = node.keys() & _filter.keys()
        if len(intersec) != len(_filter.keys()):
            return False
        for key in _filter.keys():
            filter_value = _filter[key]
            comp = node.get(key)
            if isinstance(filter_value, Mapping):
                if not self.recursive_filter(
                    comp, filter_value, depth=depth + 1
                ):
                    return False
            elif isinstance(filter_value, List):
                if comp not in filter_value:
                    return False
            elif filter_value != comp:
                return False

        return True

    def mapping_by_request_exact_match(
        self, request: Mapping[str, Any] = None
    ) -> Dict[str, Any]:
        """match mappings in wiremock using an exact match
        on the request metadata"""
        mappings = self.mappings()
        for mapping in mappings:
            if mapping["request"] == request:
                return mapping
        return None

    def populate(self, mappings: Mapping[str, Any]) -> List[Any]:
        """Populate: adds all passed mappings
        Returns the list of ids of mappings created
        """
        if isinstance(mappings, list) is False:
            logger.error("[populate]:ERROR: mappings should be a list")
            return None

        ids = []
        for mapping in mappings:
            stub_id = self.add_mapping(mapping)
            if stub_id is not None:
                ids.append(stub_id)
            else:
                logger.error("[populate]:ERROR adding a mapping")
                return None

        return ids

    def populate_from_dir(self, _dir: str) -> List[Any]:
        """reads all json files in a directory and adds all mappings
        Returns the list of ids of mappings created
        or None in case of errors
        """
        if not os.path.exists(_dir):
            logger.error(
                "[populate_from_dir]: directory %s does not exists", _dir
            )
            return None

        ids = []
        for filename in glob.glob(os.path.join(_dir, "*.json")):
            logger.info("Importing %s", filename)
            with open(filename, encoding="utf-8") as file:
                mapping = json.load(file)
                stub_id = self.add_mapping(mapping)
                if stub_id is not None:
                    ids.append(stub_id)
        return ids

    def update_fault(
        self, mappings: Mapping[str, Any], fault: str
    ) -> Optional[List[Any]]:
        """
        Updates fault status of stub mappings
        """
        if isinstance(mappings, list) is False:
            logger.error("[update_fault] mappings parameter should be a list")
            return None

        if fault not in AVAILABLE_FAULTS:
            logger.error("[update_fault] fault %s not available.", fault)
            return None

        ids = []
        for mapping in mappings:
            stub_id = mapping["id"]
            mapping["response"]["fault"] = fault

            if self.update_mapping(stub_id, mapping):
                ids.append(stub_id)
            else:
                logger.error(
                    "[populate]:ERROR updating a mapping with new fault"
                )
                return None
        return ids

    def update_status_code_and_body(
        self,
        mappings: Mapping[str, Any],
        status_code: str,
        body: str = None,
        body_file_name: str = None,
    ) -> List[Any]:
        """Populate: adds all passed mappings
        Returns the list of ids of mappings created
        """
        if isinstance(mappings, list) is False:
            logger.error("[populate]:ERROR: mappings should be a list")
            return None

        try:
            status_code_number = int(status_code)
            if status_code_number < 100 or status_code_number > 599:
                logger.error(
                    "ERROR: incorrect http status code [%s]", str(status_code)
                )
                return None
        except ValueError:
            logger.error("ERROR: incorrect http status code [%s]", status_code)
            return None

        ids = []
        for mapping in mappings:
            stub_id = mapping["id"]
            mapping["response"]["status"] = status_code
            if body_file_name:
                mapping["response"]["bodyFileName"] = body_file_name
                mapping["response"]["body"] = None
            elif body:
                mapping["response"]["bodyFileName"] = None
                mapping["response"]["body"] = body

            if self.update_mapping(stub_id, mapping):
                ids.append(stub_id)
            else:
                logger.error(
                    "[populate]:ERROR updating a mapping with new status code"
                )
                return None
        return ids

    def update_mapping(
        self, mapping_id: str = "", mapping: Mapping[str, Any] = None
    ) -> Dict[str, Any]:
        """updates the mapping pointed by id with new mapping"""
        response = requests.put(
            f"{self.mappings_url}/{mapping_id}",
            headers=self.headers,
            data=json.dumps(mapping),
            timeout=self.timeout,
        )
        if response.status_code != 200:
            logger.error("Error updating a mapping: %s", response.text)
            return None

        return response.json()

    def add_mapping(self, mapping: Mapping[str, Any]) -> int:
        """add_mapping: add a mapping passed as attribute"""
        response = requests.post(
            self.mappings_url,
            headers=self.headers,
            data=json.dumps(mapping),
            timeout=self.timeout,
        )
        if response.status_code != 201:
            logger.error("Error creating a mapping: %s", response.text)
            return None

        response_data = response.json()
        return response_data["id"]

    def delete_mapping(self, stub_id: str):
        """remove a mapping from wiremock with the requested id"""
        response = requests.delete(
            f"{self.mappings_url}/{stub_id}", timeout=self.timeout
        )
        if response.status_code != 200:
            logger.error(
                "Error deleting mapping %s: %s", stub_id, response.text
            )
            return -1

        return stub_id

    def delete_all_mappings(self):
        """deletes all mappings defined in wiremock
        returns the list of deleted mappings"""
        mappings = self.mappings()
        ids = []
        for mapping in mappings:
            stub_id = mapping["id"]
            response = requests.delete(
                f"{self.mappings_url}/{stub_id}", timeout=self.timeout
            )
            if response.status_code == 200:
                ids.append(stub_id)
            else:
                logger.error("Error deleting all mapping")

        return ids

    def fixed_delay(
        self,
        mappings: List[Mapping[str, Any]],
        fixed_delay_milliseconds: int = 0,
    ) -> Dict:
        """
        updates the mappings adding a fixed delay
        returns the a list of updated mappings or none in case of errors
        """
        updated_ids = []
        for mapping in mappings:
            m_response = mapping["response"]
            m_response["fixedDelayMilliseconds"] = fixed_delay_milliseconds
            m_response["delayDistribution"] = None
            result = self.update_mapping(mapping["id"], mapping)
            if result:
                updated_ids.append(mapping["id"])

        return updated_ids

    def global_fixed_delay(self, fixed_delay: int) -> int:
        """set a global fixed delay for all wiremock mappings"""
        response = requests.post(
            self.settings_url,
            headers=self.headers,
            data=json.dumps({"fixedDelay": fixed_delay}),
            timeout=self.timeout,
        )
        if response.status_code != 200:
            logger.error(
                "[global_fixed_delay]: Error setting delay: %s",
                response.text,
            )
            return -1

        return 1

    def random_delay(
        self, _filter: Mapping[str, Any], delay_distribution: Mapping[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates the mapping adding a random delay
        returns the updated mapping or none in case of errors
        """
        if not isinstance(delay_distribution, dict):
            logger.error("[random_delay]: parameter has to be a dictionary")

        mapping_found = self.mapping_by_request_exact_match(_filter)

        if not mapping_found:
            logger.error("[random_delay]: Error retrieving mapping")
            return None

        mapping_found["response"]["delayDistribution"] = delay_distribution
        return self.update_mapping(mapping_found["id"], mapping_found)

    def global_random_delay(
        self, delay_distribution: Mapping[str, Any]
    ) -> int:
        """set a global random delay for all wiremock mappings"""
        if not isinstance(delay_distribution, dict):
            logger.error(
                "[global_random_delay]: parameter has to be a dictionary"
            )
        response = requests.post(
            self.settings_url,
            headers=self.headers,
            data=json.dumps({"delayDistribution": delay_distribution}),
            timeout=self.timeout,
        )
        if response.status_code != 200:
            logger.error(
                "[global_random_delay]: Error setting delay: %s",
                response.text,
            )
            return -1

        return 1

    def chunked_dribble_delay(
        self,
        _filter: List[Any],
        chunked_dribble_delay: Mapping[str, Any] = None,
    ):
        """
        Adds a delay to the passed mapping
        returns the updated mapping or non in case of errors
        """
        if not isinstance(chunked_dribble_delay, dict):
            logger.error(
                "[chunked_dribble_delay]: parameter has to be a dictionary"
            )
        if "numberOfChunks" not in chunked_dribble_delay:
            logger.error(
                "[chunked_dribble_delay]: attribute numberOfChunks not "
                "found in parameter"
            )
            return None
        if "totalDuration" not in chunked_dribble_delay:
            logger.error(
                "[chunked_dribble_delay]: attribute totalDuration not found "
                "in parameter"
            )
            return None

        mapping_found = self.mapping_by_request_exact_match(_filter)

        if not mapping_found:
            logger.error("[chunked_dribble_delay]: Error retrieving mapping")
            return None

        mapping_found["response"][
            "chunkedDribbleDelay"
        ] = chunked_dribble_delay
        return self.update_mapping(mapping_found["id"], mapping_found)

    def up(self, _filter: List[Any] = None) -> List[Any]:
        """resets a list of mappings deleting all delays attached to them"""
        ids = []
        for stub_filter in _filter:
            mapping_found = self.mapping_by_request_exact_match(stub_filter)
            if mapping_found:
                logger.debug("[up]: found mapping: %s", mapping_found["id"])
                for key in [
                    "fixedDelayMilliseconds",
                    "delayDistribution",
                    "chunkedDribbleDelay",
                ]:
                    if key in mapping_found["response"]:
                        del mapping_found["response"][key]
                self.update_mapping(mapping_found["id"], mapping_found)
                ids.append(mapping_found["id"])
        return ids

    def reset(self) -> int:
        """reset global wiremock settings"""
        response = requests.post(
            self.reset_url, headers=self.headers, timeout=self.timeout
        )
        if response.status_code != 200:
            logger.error(
                "[reset]:Error resetting wiremock server %s", response.text
            )
            return -1

        return 1

    def reset_mappings(self) -> int:
        """reload wiremock mappings from disk"""
        response = requests.post(
            self.reset_mappings_url, headers=self.headers, timeout=self.timeout
        )
        if response.status_code != 200:
            logger.error(
                "[reset]:Error resetting wiremock mappings %s", response.text
            )
            return -1

        return 1
