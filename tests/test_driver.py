import unittest
from chaoswm.driver import Wiremock
from chaoswm.utils import can_connect_to


@unittest.skipUnless(
    can_connect_to(
        "localhost",
        8080),
    "Wiremock server not found")
class TestWiremock(unittest.TestCase):

    def test_add_mapping(self):
        w = Wiremock(host="localhost", port=8080, timeout=2)
        id = w.add_mapping({
            "request": {
                "method": "GET",
                "url": "/some/thing"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        })
        self.assertTrue(isinstance(id, str))
        self.assertTrue(id != -1)

    def test_update_mapping(self):
        w = Wiremock(host="localhost", port=8080, timeout=2)
        id = w.add_mapping({
            "request": {
                "method": "GET",
                "url": "/some/thing"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        })

        updated = w.update_mapping(
            id=id,
            mapping={
                "request": {
                    "method": "GET",
                    "url": "/some/thing"
                },
                "response": {
                    "status": 200,
                    "body": "Hello world!",
                    "fixedDelayMilliseconds": 10000,
                    "headers": {
                        "Content-Type": "text/plain"
                    }
                }
            }
        )
        self.assertTrue(isinstance(updated["id"], str))
        self.assertEqual(id, updated["id"])

    def test_populate(self):
        w = Wiremock(host="localhost", port=8080)
        ids = w.populate([{
            "request": {
                "method": "GET",
                "url": "/some/thing"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        }, {
            "request": {
                "method": "GET",
                "url": "/some/thing/else"
            },
            "response": {
                "status": 200,
                "body": "Hello world again!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        }])
        # the method should return a list with all the new mapping ids
        # or -1 in case of errors
        self.assertTrue(isinstance(ids, list))
        self.assertEqual(len(ids), 2)

    def test_populate_from_dir(self):
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        self.assertEqual(len(w.populate_from_dir('./tests/mappings')), 2)
        mappings = w.mappings()
        self.assertEqual(len(mappings), 2)

    def test_delete_mapping(self):
        w = Wiremock(host="localhost", port=8080)
        id = w.add_mapping({
            "request": {
                "method": "GET",
                "url": "/some/thing/to/delete"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        })
        ret = w.delete_mapping(id)
        self.assertTrue(isinstance(ret, str))
        self.assertTrue(ret != -1)

    def test_mappings(self):
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        w.add_mapping({
            "request": {
                "method": "GET",
                "url": "/some/thing/to/delete"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        })
        mappings = w.mappings()
        self.assertTrue(isinstance(mappings, list))
        self.assertEqual(len(mappings), 1)

    def test_mapping_by_id(self):
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        id = w.add_mapping({
            "request": {
                "method": "GET",
                "url": "/some/thing/to/delete"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        })
        mapping = w.mapping_by_id(id)
        self.assertTrue(isinstance(mapping, dict))
        self.assertEqual(mapping["id"], id)

    def test_mapping_by_url_and_method(self):
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        id = w.add_mapping({
            "request": {
                "method": "GET",
                "url": "/some/thing/to/delete"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        })
        mapping = w.mapping_by_url_and_method("/some/thing/to/delete", "GET")
        self.assertTrue(isinstance(mapping, dict))
        self.assertEqual(mapping["id"], id)

    def test_mapping_by_request(self):
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        self.assertEqual(len(w.populate_from_dir('./tests/mappings')), 2)
#         import pdb; pdb.set_trace()
        filter = {
            "method": "GET",
            "url": "/epg",
            "queryParameters": {"episode_title": {"matches": "([a-z]*)"}}
        }
        mapping = w.mapping_by_request(filter)
        self.assertEqual(mapping['request'], filter)

    def test_mapping_by_request_exact_match(self):
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        self.assertEqual(len(w.populate_from_dir('./tests/mappings')), 2)
#         import pdb; pdb.set_trace()
        filter = {
            "method": "GET",
            "url": "/epg"
        }
        mapping = w.mapping_by_request_exact_match(filter)
        self.assertEqual(mapping['request'], filter)

    def test_fixed_delay(self):
        #         import pdb; pdb.set_trace()
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        mapping = {
            "request": {
                "method": "GET",
                "url": "/some/delay"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        }
        id = w.add_mapping(mapping)
        delayed = w.fixed_delay(mapping['request'], 10000)
        self.assertTrue(isinstance(delayed, dict))
        self.assertTrue(isinstance(delayed["id"], str))
        self.assertEqual(delayed["id"], id)

    def test_global_fixed_delay(self):
        w = Wiremock(host="localhost", port=8080)
        ret = w.global_fixed_delay(300)
        self.assertEqual(ret, 1)

    def test_random_delay(self):
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        mapping = {
            "request": {
                "method": "GET",
                "url": "/some/thing/to/delete"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        }
        id = w.add_mapping(mapping)
        delayed = w.random_delay(
            filter=mapping['request'],
            delayDistribution={
                "type": "lognormal",
                "median": 80,
                "sigma": 0.4
            })
        self.assertTrue(isinstance(delayed['id'], str))
        self.assertEqual(delayed['id'], id)

    def test_global_random_delay(self):
        w = Wiremock(host="localhost", port=8080)
        ret = w.global_random_delay({
            "type": "lognormal",
            "median": 90,
            "sigma": 0.1
        })
        self.assertEqual(ret, 1)

    def test_chunked_dribble_delay(self):
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        mapping = {
            "request": {
                "method": "GET",
                "url": "/some/thing/to/delete"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                }
            }
        }
        id = w.add_mapping(mapping)
        delayed = w.chunked_dribble_delay(mapping["request"], {
            "numberOfChunks": 5,
            "totalDuration": 1000
        })
        self.assertTrue(isinstance(delayed, dict))
        self.assertTrue(isinstance(delayed["id"], str))
        self.assertEqual(delayed["id"], id)

        map = w.mapping_by_id(delayed["id"])
        self.assertEqual(
            map["response"]["chunkedDribbleDelay"]["totalDuration"], 1000)

    def test_up(self):
        w = Wiremock(host="localhost", port=8080)
        w.delete_all_mappings()
        mapping = {
            "request": {
                "method": "GET",
                "url": "/some/thing/to/delete"
            },
            "response": {
                "status": 200,
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                },
                "chunkedDribbleDelay": {
                    "numberOfChunks": 5,
                    "totalDuration": 1000
                }
            }
        }
        id = w.add_mapping(mapping)

        stored_mapping = w.mapping_by_id(id)
        self.assertEqual(stored_mapping["id"], id)
        self.assertEqual(
            stored_mapping["response"]["chunkedDribbleDelay"]["numberOfChunks"], 5)
        ids_up = w.up([{
            "method": "GET",
            "url": "/some/thing/to/delete"
        }])

        up_mapping = w.mapping_by_id(ids_up[0])
        self.assertFalse("chunkedDribbleDelay" in up_mapping["response"])

    def test_reset(self):
        w = Wiremock(host="localhost", port=8080)
        self.assertEqual(w.reset(), 1)
