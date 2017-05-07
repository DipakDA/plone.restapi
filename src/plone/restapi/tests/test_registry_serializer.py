# -*- coding: utf-8 -*-
import unittest

from plone.registry import Registry
from plone.registry import field
from plone.registry.record import Record
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from zope.component import getMultiAdapter


class TestRegistrySerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def serialize(self, obj):
        serializer = getMultiAdapter((obj, self.request),
                                     ISerializeToJson)
        return serializer()

    def test_empty(self):
        registry = Registry()
        obj = self.serialize(registry)
        expected = ['@id', 'items_total', 'items']
        self.assertEqual(set(obj.keys()), set(expected))
        self.assertNotIn('batching', obj.keys())

    def test_batched(self):
        registry = Registry()

        for counter in range(1, 100):
            record = Record(field.TextLine(title=u"Foo Bar"), u"Lorem Ipsum")
            registry.records['foo.bar' + str(counter)] = record

        obj = self.serialize(registry)
        expected = ['@id', 'items_total', 'items', 'batching']
        self.assertEqual(set(expected), set(obj.keys()))
        self.assertEqual(obj['items_total'], len(range(1, 100)))

    def test_structure(self):
        registry = Registry()

        record = Record(field.TextLine(title=u"Foo Bar"), u"Lorem Ipsum")
        registry.records['foo.bar'] = record

        obj = self.serialize(registry)
        item = obj['items'][0]
        self.assertEqual(set(item.keys()), set(['name', 'value']))
        self.assertEqual(item['name'], 'foo.bar')
        self.assertEqual(item['value'], u"Lorem Ipsum")
