import redis
import unittest
from hotels import hotels
import random
import time
import unittest
from base_case import BaseSearchTestCase


def testBasicPoneticCase(self):
    self.assertOk(self.cmd('ft.create', 'idx', 'schema', 'text', 'TEXT', 'PHONETIC', 'dm:en', 'SORTABLE'))
    self.assertOk(self.cmd('ft.add', 'idx', 'doc1', 1.0, 'fields',
                           'text', 'morfix'))

    self.assertEquals(self.cmd('ft.search', 'idx', 'morphix'), [1L, 'doc1', ['text', 'morfix']])
    self.assertEquals(self.cmd('ft.search', 'idx', '@text:morphix'), [1L, 'doc1', ['text', 'morfix']])
    self.assertEquals(self.cmd('ft.search', 'idx', '@text:morphix=>{$phonetic:true}'), [1L, 'doc1', ['text', 'morfix']])
    self.assertEquals(self.cmd('ft.search', 'idx', '@text:morphix=>{$phonetic:false}'), [0L])

def testBasicPoneticWrongDeclaration(self):
    with self.assertResponseError():
        self.cmd('ft.create', 'idx', 'schema', 'text', 'TEXT', 'PHONETIC', 'something', 'SORTABLE')
    with self.assertResponseError():
        self.cmd('ft.create', 'idx', 'schema', 'text', 'TEXT', 'PHONETIC', 'kk:tt', 'SORTABLE')
    with self.assertResponseError():
        self.cmd('ft.create', 'idx', 'schema', 'text', 'TEXT', 'PHONETIC', 'dm:tt', 'SORTABLE')
    with self.assertResponseError():
        self.cmd('ft.create', 'idx', 'schema', 'text', 'TEXT', 'PHONETIC', 'll:en', 'SORTABLE')

def testPoneticOnNonePhoneticField(self):
    self.assertOk(self.cmd('ft.create', 'idx', 'schema', 'text', 'TEXT', 'PHONETIC', 'dm:en', 'SORTABLE', 'text1', 'TEXT', 'SORTABLE'))
    self.assertOk(self.cmd('ft.add', 'idx', 'doc1', 1.0, 'fields',
                           'text', 'morfix',
                           'text1', 'phonetic'))

    self.assertEquals(self.cmd('ft.search', 'idx', 'morphix'), [1L, 'doc1', ['text', 'morfix', 'text1', 'phonetic']])
    self.assertEquals(self.cmd('ft.search', 'idx', '@text:morphix'), [1L, 'doc1', ['text', 'morfix', 'text1', 'phonetic']])
    self.assertEquals(self.cmd('ft.search', 'idx', 'phonetic'), [1L, 'doc1', ['text', 'morfix', 'text1', 'phonetic']])
    self.assertEquals(self.cmd('ft.search', 'idx', 'fonetic'), [0L])
    self.assertEquals(self.cmd('ft.search', 'idx', '@text1:morphix'), [0L])
    with self.assertResponseError():
        self.cmd('ft.search', 'idx', '@text1:morphix=>{$phonetic:true}')
    with self.assertResponseError():
        self.cmd('ft.search', 'idx', '@text1:morphix=>{$phonetic:false}')

def testPoneticWithAggregation(self):
    self.assertOk(self.cmd('ft.create', 'idx', 'schema', 'text', 'TEXT', 'PHONETIC', 'dm:en', 'SORTABLE', 'text1', 'TEXT', 'SORTABLE'))
    self.assertOk(self.cmd('ft.add', 'idx', 'doc1', 1.0, 'fields',
                           'text', 'morfix',
                           'text1', 'phonetic'))

    self.assertEquals(self.cmd('ft.aggregate', 'idx', 'morphix', 'LOAD', 2, '@text', '@text1'), [1L, ['text', 'morfix', 'text1', 'phonetic']])
    self.assertEquals(self.cmd('ft.aggregate', 'idx', '@text:morphix', 'LOAD', 2, '@text', '@text1'), [1L, ['text', 'morfix', 'text1', 'phonetic']])
    self.assertEquals(self.cmd('ft.aggregate', 'idx', 'phonetic', 'LOAD', 2, '@text', '@text1'), [1L, ['text', 'morfix', 'text1', 'phonetic']])
    self.assertEquals(self.cmd('ft.aggregate', 'idx', '@text1:morphix', 'LOAD', 2, '@text', '@text1'), [0L])
    if not self.is_cluster():
        with self.assertResponseError():
            self.cmd('ft.aggregate', 'idx', '@text1:morphix=>{$phonetic:true}')
        with self.assertResponseError():
            self.cmd('ft.aggregate', 'idx', '@text1:morphix=>{$phonetic:false}')
    else:
        raise unittest.SkipTest("FIXME: Aggregation error propagation broken on cluster mode")

def testPoneticWithSchemaAlter(self):
    self.assertOk(self.cmd('ft.create', 'idx', 'schema', 'text', 'TEXT', 'PHONETIC', 'dm:en', 'SORTABLE', 'text1', 'TEXT', 'SORTABLE'))
    self.assertOk(self.cmd('ft.alter', 'idx', 'SCHEMA', 'ADD', 'text2', 'TEXT', 'PHONETIC', 'dm:en'))

    self.assertOk(self.cmd('ft.add', 'idx', 'doc1', 1.0, 'fields',
                           'text', 'morfix',
                           'text1', 'check',
                           'text2', 'phonetic'))

    self.assertEquals(self.cmd('ft.search', 'idx', 'fonetic'), [1L, 'doc1', ['text', 'morfix', 'text1', 'check', 'text2', 'phonetic']])
    self.assertEquals(self.cmd('ft.search', 'idx', '@text2:fonetic'), [1L, 'doc1', ['text', 'morfix', 'text1', 'check', 'text2', 'phonetic']])
    self.assertEquals(self.cmd('ft.search', 'idx', '@text1:fonetic'), [0L])
    self.assertEquals(self.cmd('ft.search', 'idx', '@text2:fonetic=>{$phonetic:false}'), [0L])
    self.assertEquals(self.cmd('ft.search', 'idx', '@text2:fonetic=>{$phonetic:true}'), [1L, 'doc1', ['text', 'morfix', 'text1', 'check', 'text2', 'phonetic']])

def testPoneticWithSmallTerm(self):
    self.assertOk(self.cmd('ft.create', 'complainants', 'SCHEMA', 'name', 'text', 'PHONETIC', 'dm:en', 'almamater', 'text', 'PHONETIC', 'dm:en'))

    self.assertOk(self.cmd('ft.add', 'complainants', 'foo64', 1.0, 'FIELDS', 'name', 'jon smith', 'almamater', 'Trent'))
    self.assertOk(self.cmd('ft.add', 'complainants', 'foo65', 1.0, 'FIELDS', 'name', 'john jones', 'almamater', 'Toronto'))

    res = self.cmd('ft.search', 'complainants', '@name:(john=>{$phonetic:true})')
    self.assertEqual(res, [2L, 'foo64', ['name', 'jon smith', 'almamater', 'Trent'], 'foo65', ['name', 'john jones', 'almamater', 'Toronto']])
