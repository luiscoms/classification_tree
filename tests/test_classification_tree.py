#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests_mock
import unittest
from ddt import ddt, data, file_data, unpack

from classification_tree import ClassificationTree

@ddt
class ClassificationTreeTest(unittest.TestCase):

    tree = [
      {
        "_id": "001",
        "name": "First level",
        "items": [
          {
            "_id": "002",
            "name": "Second level - first",
            "parent": "001",
            "items": [
              {
                "_id": "003",
                "name": "Third level - first",
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
                    "parent": "003"
                  }
                ]
              }
            ]
          },
          {
            "_id": "010",
            "name": "Second level - second",
            "parent": "001",
            "items": [
              {
                "_id": "011",
                "name": "Third level - first",
                "parent": "010",
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
    @requests_mock.mock()
    def setUp(self, mock):
        mock.get(
            'http://classifications-api.com.br/tree',
            json=self.tree)
        self.ct = ClassificationTree('http://classifications-api.com.br/')

    @unpack
    @data(([], None))
    def test_get_hierarchy_shoud_return_empty_with_invalid_id(self, expected, input_value):
        self.assertEqual(expected, self.ct.get_hierarchy(input_value))

    @unpack
    @data(
        ([{'_id': '001', 'name': 'First level'}], '001'),
        # expected
        ([{'_id': '001', 'name': 'First level'},
          {'_id': '010', 'name': 'Second level - second', 'parent': '001'}],
          # input_value
          '010'),
        # expected
        ([{'_id': '001', 'name': 'First level'},
          {'_id': '010', 'name': 'Second level - second', 'parent': '001'},
          {"_id": "015", "name": "Third level - second", "parent": "010"}],
          # input_value
          '015'),
        # expected
        ([{'_id': '001', 'name': 'First level'},
          {'_id': '002', 'name': 'Second level - first', 'parent': '001'},
          {"_id": "003", "name": "Third level - first", "parent": "002"},
          {"_id": "006", "name": "Fourth level - third", "parent": "003"}],
          # input_value
          '006'),
    )
    def test_get_hierarchy_shoud_return_list_with_valid_id(self, expected, input_value):
        self.assertEqual(expected, self.ct.get_hierarchy(input_value))


if __name__ == '__main__':
    unittest.main()
