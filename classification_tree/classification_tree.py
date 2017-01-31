#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module show."""
import logging
import requests

__all__ = ['ClassificationTree']


class ClassificationTree(object):
    """Get classification tree from service.

    Usage:
    >>> ct = ClassificationTree('http://classifications-api.com.br')
    >>> ct.get_hierarchy('classification_id')
    []
    """

    classifications_hashmap = {}
    logger = None

    def __init__(self, api_url='http://classifications-api.com.br/', logger=logging.getLogger(__name__)):
        """Constructor."""
        self.logger = logger
        self.logger.debug("init ClassificationTree")

        tree = {}
        try:
            # get classifications tree from api
            tree = requests.get(api_url.rstrip('/') + '/tree').json()
            # self.logger.debug(tree)
        except Exception as e:
            self.logger.error(e)

        for classification in tree:
            # call recursively
            self.__tree2dict(classification)

    def __tree2dict(self, classification):
        """Create a hashmap from classifications."""
        if not type(classification) is dict:
            self.logger.error('classification is not a dict')
            return
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
        the_dict = {
            'slug': found_element['slug'],
            'id': found_element['_id'],
            'items': found_element.get('items', []),
            'name': found_element.get('name', [])
        }
        return the_dict

    def parse_tree(self, data, slugs):
        for slug in slugs:
            the_dict = self.filter_by_slug(slug, data)
            data = the_dict['items']
        return the_dict

    def extract_id_by_slug(self, the_json, path):
        the_dict = {}
        try:
            the_dict = self.parse_tree(the_json, path.split('/'))
        except Exception as e:
            self.logger.error("Couldn't find an id for this path: %s", path)
        return the_dict

    def get_id_by_slug(self, classifications, api_url='http://classifications-api.com.br/'):
        tree = {}
        try:
            tree = requests.get(api_url + '/tree').json()
        except Exception as e:
            self.logger.error(e, exc_info=True)
        return self.extract_id_by_slug(tree, classifications)

    def get_slug_by_id(self, classification_id):
        hierarchy = self.get_hierarchy(classification_id)
        slug = ''
        for data in hierarchy:
            slug += data.get('slug', '') + '/'
        return slug

    def get_section_url(self, classification_id):
        """Return the last url found."""
        hierarchy = self.get_hierarchy(classification_id)

        # return the last url found
        filtered = list(filter(lambda c: c.get('url'), hierarchy))
        return ([{}] + filtered)[-1:][0].get('url')
