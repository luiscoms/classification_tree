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
        "type": "main-type",
        "items": [
            {
                "_id": "002",
                "name": "Second level - first",
                "slug": "second-level-first",
                "parent": "001",
                "type": "other-type",
                "items": [
                    {
                        "_id": "003",
                        "name": "Third level - first",
                        "slug": "third-level-first",
                        "parent": "002",
                        "type": "section",
                        "items": [
                            {
                                "_id": "004",
                                "name": "Fourth level - first",
                                "slug": "fourth-level-first",
                                "parent": "003"
                            },
                            {
                                "_id": "005",
                                "name": "Fourth level - second",
                                "slug": "fourth-level-second",
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
                "type": "other-type",
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
                        "parent": "010",
                        "slug": "third-level-second",
                        "type": "another-type"
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

            self.setUpMock(child, i + 1)

    @unpack
    @data(([], None))
    def test_get_hierarchy_shoud_return_empty_with_invalid_id(self, expected, input_value):
        self.assertEqual(expected, self.ct.get_hierarchy(input_value))

    @unpack
    @data(
        ([{'_id': '001', 'name': 'First level', "slug": "first-level", "type": "main-type"}], '001'),
        # expected
        ([{'_id': '001', 'name': 'First level', "slug": "first-level", "type": "main-type"},
          {'_id': '010', 'name': 'Second level - second', 'parent': '001',
           'url': "some.parent.url", "slug": "second-level-second", "type": "other-type"}],
         # input_value
         '010'),
        # expected
        ([{'_id': '001', 'name': 'First level', "slug": "first-level", "type": "main-type"},
          {'_id': '010', 'name': 'Second level - second', 'parent': '001',
           'url': "some.parent.url", "slug": "second-level-second", "type": "other-type"},
          {"_id": "015", "name": "Third level - second", "parent": "010", "slug": "third-level-second",
           "type": "another-type"}],
         # input_value
         '015'),
        # expected
        ([{'_id': '001', 'name': 'First level', "slug": "first-level", "type": "main-type"},
          {'_id': '002', 'name': 'Second level - first', 'parent': '001', "slug": "second-level-first",
           "type": "other-type"},
          {"_id": "003", "name": "Third level - first", "parent": "002", "slug": "third-level-first",
           "type": "section"},
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
        ([{"_id": "015", "name": "Third level - second", "parent": "010", "slug": "third-level-second",
           "type": "another-type"}], ["015"]),
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
        (mock_tree[0]['items'][0]['items'][0], "first-level/second-level-first/third-level-first"),
        (mock_tree[0]['items'][0]['items'][0]['items'][2],
         "first-level/second-level-first/third-level-first/fourth-level-third"),
    )
    @httpretty.activate
    def test_get_id_by_slug(self, expected, input_value):
        self.setUpMock(mock_tree)
        ret = self.ct.get_id_by_slug(input_value)
        self.assertEqual(expected, ret)

    @data(
        (list(), list()),
        (["001"], ["001"]),
        (["001", "002"], ["002"]),
        (["001", "002", "003"], ["003"]),
        (["001", "002", "003", "004"], ["004"]),
        (["001", "002", "003", "004"], ["004", "004"]),  # repeated values
        (["001", "002", "003", "004", "010", "011", "012"], ["004", "012"]),
    )
    @unpack
    @httpretty.activate
    def test_get_all_classifications(self, expected, input_value):
        self.setUpMock(mock_tree)
        ret = self.ct.get_all_classifications(input_value)
        self.assertEqual(len(expected), len(ret))
        for expected_id in expected:
            self.assertIn(expected_id, ret)

    @data(
        ("first-level", "001"),
        ("first-level/second-level-first", "002"),
        ("first-level/second-level-second", "010"),
        ("first-level/second-level-first/third-level-first", "003"),
        ("first-level/second-level-second/third-level-second", "015"),
    )
    @unpack
    @httpretty.activate
    def test_get_slug_by_id(self, expected, input_value):
        self.setUpMock(mock_tree)
        ret = self.ct.get_slug_by_id(input_value)
        self.assertEqual(expected, ret)

    @data(
        ("first-level", "001", ["main-type"]),
        ("", "001", ["other-type"]),
        ("first-level/second-level-first", "002", ["main-type", "other-type"]),
        ("second-level-first", "002", ["other-type"]),
        ("", "002", ["main-type"]),
        ("first-level/second-level-second/third-level-second", "015", ["main-type", "other-type", "another-type"]),
        ("second-level-second/third-level-second", "015", ["other-type", "another-type"]),
        ("third-level-second", "015", ["another-type"]),
        ("", "015", ["invalid-type"]),
    )
    @unpack
    @httpretty.activate
    def test_get_slug_by_id_with_filter(self, expected, input_value, types_in):
        self.setUpMock(mock_tree)
        ret = self.ct.get_slug_by_id(input_value, types_in)
        self.assertEqual(expected, ret)


if __name__ == '__main__':
    unittest.main()
