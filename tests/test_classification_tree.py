#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import unittest

from ddt import ddt, data, unpack

from classification_tree import ClassificationTree

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import httpretty

mock_tree = [
    {
        "_id": "001",
        "name": "First level",
        "slug": "first-level",
        "items": [
            {
                "_id": "002",
                "name": "Second level - first",
                "slug": "second-level-first",
                "parent": "001",
                "items": [
                    {
                        "_id": "003",
                        "name": "Third level - first",
                        "slug": "third-level-first",
                        "parent": "002",
                        "items": [
                            {
                                "_id": "004",
                                "name": "Fourth level - first",
                                "parent": "003"
                            },
                            {
                                "_id": "005",
                                "name": "Fourth level - second",
                                "parent": "003"
                            },
                            {
                                "_id": "006",
                                "name": "Fourth level - third",
                                "slug": "fourth-level-third",
                                "parent": "003"
                            }
                        ]
                    }
                ]
            },
            {
                "_id": "010",
                "name": "Second level - second",
                "slug": "second-level-second",
                "parent": "001",
                "url": "some.parent.url",
                "items": [
                    {
                        "_id": "011",
                        "name": "Third level - first",
                        "parent": "010",
                        "url": "some.url",
                        "items": [
                            {
                                "_id": "012",
                                "name": "Fourth level - first",
                                "parent": "011"
                            },
                            {
                                "_id": "013",
                                "name": "Fourth level - second",
                                "parent": "011"
                            },
                            {
                                "_id": "014",
                                "name": "Fourth level - third",
                                "parent": "011"
                            },
                        ]
                    },
                    {
                        "_id": "015",
                        "name": "Third level - second",
                        "parent": "010"
                    }
                ]
            }
        ]
    }
]


@ddt
class ClassificationTreeTest(unittest.TestCase):
    maxDiff = None

    @httpretty.activate
    def setUp(self):
        self.setUpMockTree()
        self.setUpMock(mock_tree)
        self.ct = ClassificationTree('http://classifications-api.com.br/')

    def setUpMockTree(self):
        httpretty.register_uri(httpretty.GET,
                               "http://classifications-api.com.br/tree",
                               content_type="application/json",
                               body=json.dumps(mock_tree))

    def setUpMock(self, tree, i=0):
        if i >= 3 or not tree:
            return

        for item in tree:
            data = item.copy()
            child = data.pop('items', [])

            # query string
            qs = {
                "where": json.dumps({
                    "_id": {
                        "$in": [data['_id']]
                    }
                }, separators=(',', ':'))
            }
            body = json.dumps({"_items": [data]})
            httpretty.register_uri(httpretty.GET,
                                   "http://classifications-api.com.br/?{}".format(urlencode(qs)),
                                   # "http://classifications-api.com.br?where={}".format(qs["where"]),
                                   content_type="application/json",
                                   match_querystring=True,
                                   body=body)

            self.setUpMock(child, i+1)

    @unpack
    @data(([], None))
    def test_get_hierarchy_shoud_return_empty_with_invalid_id(self, expected, input_value):
        self.assertEqual(expected, self.ct.get_hierarchy(input_value))

    @unpack
    @data(
        ([{'_id': '001', 'name': 'First level', "slug": "first-level"}], '001'),
        # expected
        ([{'_id': '001', 'name': 'First level', "slug": "first-level"},
          {'_id': '010', 'name': 'Second level - second', 'parent': '001',
           'url': "some.parent.url", "slug": "second-level-second"}],
         # input_value
         '010'),
        # expected
        ([{'_id': '001', 'name': 'First level', "slug": "first-level"},
          {'_id': '010', 'name': 'Second level - second', 'parent': '001',
           'url': "some.parent.url", "slug": "second-level-second"},
          {"_id": "015", "name": "Third level - second", "parent": "010"}],
         # input_value
         '015'),
        # expected
        ([{'_id': '001', 'name': 'First level', "slug": "first-level"},
          {'_id': '002', 'name': 'Second level - first', 'parent': '001', "slug": "second-level-first"},
          {"_id": "003", "name": "Third level - first", "parent": "002", "slug": "third-level-first"},
          {"_id": "006", "name": "Fourth level - third", "parent": "003", "slug": "fourth-level-third"}],
         # input_value
         '006'),
    )
    def test_get_hierarchy_shoud_return_list_with_valid_id(self, expected, input_value):
        self.assertEqual(expected, self.ct.get_hierarchy(input_value))

    @unpack
    @data(
        (None, None),
        (None, "004"),
        ("some.url", "012"),
        ("some.parent.url", "015"),
    )
    def test_get_section_url_should_return_last_url(self, expected, input_value):
        self.assertEqual(expected, self.ct.get_section_url(input_value))

    @unpack
    @data(
        ([], None),
        ([], []),
        ([{"_id": "015", "name": "Third level - second", "parent": "010", }], ["015"]),
        # ([{"_id": "002", 'name': "Second level - first", "parent": "001", "slug": "second-level-first"}], ["002"]),
    )
    @httpretty.activate
    def test_get_list_by_ids_should_return_list(self, expected, input_value):
        self.setUpMock(mock_tree)
        self.assertEqual(expected, self.ct.get_list_by_ids(input_value))

    @unpack
    @data(
        (dict(), "invalid"),
        (mock_tree[0], "first-level"),
        (mock_tree[0]['items'][0], "first-level/second-level-first"),
    )
    @httpretty.activate
    def test_get_id_by_slug(self, expected, input_value):
        self.setUpMock(mock_tree)
        ret = self.ct.get_id_by_slug(input_value)
        self.assertEqual(expected, ret)


if __name__ == '__main__':
    unittest.main()
