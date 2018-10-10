#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name: ClassificationTree
Version: 1.5.0
"""
import json
import logging
import requests
import warnings

__all__ = ['ClassificationTree']


class ClassificationTree(object):
    """Get classification tree from service.

    Usage:
    >>> ct = ClassificationTree('http://classifications-api.com.br')
    >>> ct.get_hierarchy('classification_id')
    []
    """

    tree = {}
    classifications_hashmap = {}
    types = []
    logger = None

    def __init__(self, api_url='http://classifications-api.com.br/', logger=logging.getLogger(__name__)):
        """Constructor."""
        self.url = api_url.rstrip('/')
        self.logger = logger
        self.logger.debug("init ClassificationTree")

        try:
            # get classifications tree from api
            self.tree = requests.get(api_url.rstrip('/') + '/tree').json()
            # self.logger.debug(tree)
        except Exception as e:
            self.logger.error(e)

        for classification in self.tree:
            # call recursively
            self.__tree2dict(classification)

        # set all types found
        self.types = set(filter(lambda t: t, self.types))

    def __tree2dict(self, classification):
        """Create a hashmap from classifications."""
        if not type(classification) is dict:
            self.logger.error('classification is not a dict')
            return
        self.types += [classification.get('type')]
        self.classifications_hashmap[classification['_id']] = classification
        for _classification in classification.get('items', []):
            self.__tree2dict(_classification)

    def get_hierarchy(self, classification_id):
        """Return a list of classifications."""
        if not classification_id:
            return []
        classification = self.classifications_hashmap.get(classification_id, {})
        if not classification:
            self.logger.warning("classification not found on tree %s", classification_id)
            return []
        classification.pop('items', None)
        return self.get_hierarchy(classification.get('parent')) + [classification]

    def filter_by_slug(self, slug, the_json):
        found_element = list(filter(lambda x: x['slug'] == slug, the_json))[0]
        return found_element.copy()

    def parse_tree(self, data, slugs):
        for slug in slugs:
            the_dict = self.filter_by_slug(slug, data)
            data = the_dict.get('items', [])
        return the_dict

    def extract_id_by_slug(self, the_json, path):
        the_dict = {}
        try:
            the_dict = self.parse_tree(the_json, path.split('/'))
        except Exception as e:
            self.logger.error("Couldn't find an id for this path: %s (%s)", path, e)
        return the_dict

    def get_id_by_slug(self, classifications, api_url=None):
        if api_url:
            self.logger.warning("Deprecated parameter api_url")
            warnings.warn("Deprecated parameter api_url", DeprecationWarning)
        return self.extract_id_by_slug(self.tree, classifications)

    def get_slug_by_id(self, classification_id, types_in=None):
        hierarchy = self.get_hierarchy(classification_id)
        if not hierarchy:
            return ""
        types_in = types_in or self.types
        if hierarchy[-1]['type'] not in types_in:
            return ""
        return '/'.join(
            list(map(lambda x: x['slug'], filter(lambda y: y['type'] in types_in, hierarchy)))
        )

    def get_section_url(self, classification_id):
        """Return the last url found."""
        hierarchy = self.get_hierarchy(classification_id)

        # return the last url found
        filtered = list(filter(lambda c: c.get('url'), hierarchy))
        return ([{}] + filtered)[-1:][0].get('url')

    def get_list_by_ids(self, classification_ids):
        """Get all classifications by id from classifications-api."""
        # self.logger.debug("getting classifications %s", classification_ids)
        if type(classification_ids) is not list or len(classification_ids) <= 0:
            return []

        where = {
            "where": json.dumps({
                "_id": {
                    "$in": classification_ids
                }
            }, separators=(',', ':'))
        }
        res = requests.get(
            self.url,
            params=where).json()['_items']
        return res

    def get_all_classifications(self, classifications_ids):
        """Return a list of hierarchy classifications given a list if classifications."""
        all_classifications = []

        for classification in classifications_ids:
            classification_hierarchy = self.get_hierarchy(classification)
            classifications_id = list(map(lambda x: x['_id'], classification_hierarchy))
            all_classifications += classifications_id

        return list(set(all_classifications))
