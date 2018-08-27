import time
import unittest
import os.path

from base_case import BaseSearchTestCase

GENTEXT = os.path.dirname(os.path.abspath(__file__)) + '/../tests/genesis.txt'


def setupGenesis(self):
    txt = open(GENTEXT, 'r').read()
    self.cmd('ft.create', 'idx', 'schema', 'txt', 'text')
    self.cmd('ft.add', 'idx', 'gen1', 1.0, 'fields', 'txt', txt)

def testSummarization(self):
    # Load the file
    setupGenesis(self)
    res = self.cmd('FT.SEARCH', 'idx', 'abraham isaac jacob',
                   'SUMMARIZE', 'FIELDS', 1, 'txt', 'LEN', 20,
                   'HIGHLIGHT', 'FIELDS', 1, 'txt', 'TAGS', '<b>', '</b>')
    self.assertEqual(1, res[0])
    # print res
    res_txt = res[2][1]
    # print res_txt

    self.assertTrue("<b>Abraham</b>" in res_txt)
    self.assertTrue("<b>Isaac</b>" in res_txt)
    self.assertTrue("<b>Jacob</b>" in res_txt)

    res = self.cmd('FT.SEARCH', 'idx', 'abraham isaac jacob',
                   'HIGHLIGHT', 'fields', 1, 'txt', 'TAGS', '<i>', '</i>')
    res_txt = res[2][1]
    self.assertGreaterEqual(len(res_txt), 160000)

    res = self.cmd('FT.SEARCH', 'idx', 'abraham isaac jacob',
                   'SUMMARIZE', 'FIELDS', 1, 'txt', 'FRAGS', 10000)
    # print res

    res_list = res[2][1]
    # self.assertIsInstance(res_list, list)

    # Search with custom separator
    res = self.cmd('FT.SEARCH', 'idx', 'isaac',
                   'SUMMARIZE', 'FIELDS', 1, 'txt',
                   'SEPARATOR', '\r\n',
                   'FRAGS', 4, 'LEN', 3)
    self.assertEqual([1L, 'gen1', [
                     'txt', 'name Isaac: and\r\nwith Isaac,\r\nIsaac. {21:4} And Abraham circumcised his son Isaac\r\nson Isaac was\r\n']], res)

    # Attempt a query which doesn't have a corresponding matched term
    res = self.cmd('FT.SEARCH', 'idx', '-blah', 'SUMMARIZE', 'LEN', 3)
    self.assertEqual(
        [1L, 'gen1', ['txt', ' The First Book of Moses, called Genesis {1:1} In']], res)

    # Try the same, but attempting to highlight
    res = self.cmd('FT.SEARCH', 'idx', '-blah', 'HIGHLIGHT')
    self.assertEqual(214894, len(res[2][1]))

def testPrefixExpansion(self):
    # Search with prefix
    setupGenesis(self)
    res = self.cmd('FT.SEARCH', 'idx', 'begi*',
                   'HIGHLIGHT', 'FIELDS', 1, 'txt', 'TAGS', '<b>', '</b>',
                   'SUMMARIZE', 'FIELDS', 1, 'txt', 'LEN', 20)

    # Prefix expansion uses "early exit" strategy, so the term highlighted won't necessarily be the
    # best term
    self.assertEqual([1L, 'gen1', [
                     'txt', 'is] one, and they have all one language; and this they <b>begin</b> to do: and now nothing will be restrained from them, which... ']], res)
    # self.assertEqual([1L, 'gen1', ['txt', 'First Book of Moses, called Genesis {1:1} In the <b>beginning</b> God created the heaven and the earth. {1:2} And the earth... the mighty hunter before the LORD. {10:10} And the <b>beginning</b> of his kingdom was Babel, and Erech, and Accad, and Calneh... is] one, and they have all one language; and this they <b>begin</b> to do: and now nothing will be restrained from them, which... ']], res)

def testSummarizationMultiField(self):
    p1 = "Redis is an open-source in-memory database project implementing a networked, in-memory key-value store with optional durability. Redis supports different kinds of abstract data structures, such as strings, lists, maps, sets, sorted sets, hyperloglogs, bitmaps and spatial indexes. The project is mainly developed by Salvatore Sanfilippo and is currently sponsored by Redis Labs.[4] Redis Labs creates and maintains the official Redis Enterprise Pack."
    p2 = "Redis typically holds the whole dataset in memory. Versions up to 2.4 could be configured to use what they refer to as virtual memory[19] in which some of the dataset is stored on disk, but this feature is deprecated. Persistence is now achieved in two different ways: one is called snapshotting, and is a semi-persistent durability mode where the dataset is asynchronously transferred from memory to disk from time to time, written in RDB dump format. Since version 1.1 the safer alternative is AOF, an append-only file (a journal) that is written as operations modifying the dataset in memory are processed. Redis is able to rewrite the append-only file in the background in order to avoid an indefinite growth of the journal."

    self.cmd('FT.CREATE', 'idx', 'SCHEMA', 'txt1', 'TEXT', 'txt2', 'TEXT')
    self.cmd('FT.ADD', 'idx', 'redis', 1.0,
             'FIELDS', 'txt1', p1, 'txt2', p2)

    # Now perform the multi-field search
    self.cmd('FT.SEARCH', 'idx', 'memory persistence salvatore',
             'HIGHLIGHT', 'TAGS', '<b>', '</b>',
             'SUMMARIZE', 'LEN', 5,
             'RETURN', 2, 'txt1', 'txt2')

    # Now perform the multi-field search
    res = self.cmd('FT.SEARCH', 'idx', 'memory persistence salvatore',
                   'SUMMARIZE', 'FIELDS', 2, 'txt1', 'txt2', 'LEN', 5)
    # print res
    self.assertEqual([1L, 'redis', ['txt1', 'memory database project implementing a networked, in-memory ... by Salvatore Sanfilippo... ', 'txt2',
                                    'dataset in memory. Versions... as virtual memory[19] in... persistent durability mode where the dataset is asynchronously transferred from memory... ']], res)

def testSummarizationDisabled(self):
    self.cmd('FT.CREATE', 'idx', 'NOOFFSETS', 'SCHEMA', 'body', 'TEXT')
    self.cmd('FT.ADD', 'idx', 'doc', 1.0, 'FIELDS', 'body', 'hello world')
    with self.assertResponseError():
        res = self.cmd('FT.SEARCH', 'idx', 'hello',
                       'SUMMARIZE', 'FIELDS', 1, 'body')

    self.cmd('FT.CREATE', 'idx2', 'NOHL', 'SCHEMA', 'body', 'TEXT')
    self.cmd('FT.ADD', 'idx2', 'doc', 1.0, 'FIELDS', 'body', 'hello world')
    with self.assertResponseError():
        res = self.cmd('FT.SEARCH', 'idx2', 'hello',
                       'SUMMARIZE', 'FIELDS', 1, 'body')

def testSummarizationNoSave(self):
    self.cmd('FT.CREATE', 'idx', 'SCHEMA', 'body', 'TEXT')
    self.cmd('FT.ADD', 'idx', 'doc', 1.0, 'NOSAVE',
             'fields', 'body', 'hello world')
    res = self.cmd('FT.SEARCH', 'idx', 'hello',
                   'SUMMARIZE', 'RETURN', 1, 'body')
    # print res
    self.assertEqual([1L, 'doc', ['body', None]], res)

def testSummarizationMeta(self):
    self.cmd('ft.create', 'idx', 'schema', 'foo',
             'text', 'bar', 'text', 'baz', 'text')
    self.cmd('ft.add', 'idx', 'doc1', 1.0, 'fields', 'foo',
             'pill', 'bar', 'pillow', 'baz', 'piller')

    # Now, return the fields:
    res = self.cmd('ft.search', 'idx', 'pill pillow piller',
                   'RETURN', 1, 'baz', 'SUMMARIZE', 'FIELDS', 2, 'foo', 'bar')
    self.assertEqual(1, res[0])
    result = res[2]
    names = [x[0] for x in grouper(result, 2)]

    # RETURN restricts the number of fields
    self.assertEqual(set(('baz',)), set(names))

    res = self.cmd('ft.search', 'idx', 'pill pillow piller',
                   'RETURN', 3, 'foo', 'bar', 'baz', 'SUMMARIZE')
    self.assertEqual([1L, 'doc1', ['foo', 'pill... ', 'bar',
                                   'pillow... ', 'baz', 'piller... ']], res)


def testOverflow1(self):
    #"FT.CREATE" "netflix" "SCHEMA" "title" "TEXT" "WEIGHT" "1" "rating" "TEXT" "WEIGHT" "1" "level" "TEXT" "WEIGHT" "1" "description" "TEXT" "WEIGHT" "1" "year" "NUMERIC" "uscore" "NUMERIC" "usize" "NUMERIC"
    #FT.ADD" "netflix" "15ad80086ccc7f" "1" "FIELDS" "title" "The Vampire Diaries" "rating" "TV-14" "level" "Parents strongly cautioned. May be unsuitable for children ages 14 and under." "description" "90" "year" "2017" "uscore" "91" "usize" "80"
    self.cmd('FT.CREATE', 'netflix', 'SCHEMA', 'title', 'TEXT', 'rating', 'TEXT', 'leve', 'TEXT', 'description', 'TEXT', 'year', 'NUMERIC', 'uscore', 'NUMERIC', 'usize', 'NUMERIC')
    self.cmd('FT.ADD', "netflix", "15ad80086ccc7f", "1.0", "FIELDS", "title", "The Vampire Diaries", "rating", "TV-14", "level",
        "Parents strongly cautioned. May be unsuitable for children ages 14 and under.",
        "description", "90", "year", "2017", "uscore", "91", "usize", "80")
    res = self.cmd('ft.search', 'netflix', 'vampire', 'highlight')
    self.assertEqual([1L, '15ad80086ccc7f', ['title', 'The <b>Vampire</b> Diaries', 'rating', 'TV-14', 'level', 'Parents strongly cautioned. May be unsuitable for children ages 14 and under.', 'description', '90', 'year', '2017', 'uscore', '91', 'usize', '80']], res)
    
def testIssue364(self):
    # FT.CREATE testset "SCHEMA" "permit_timestamp" "NUMERIC" "SORTABLE" "job_category" "TEXT" "NOSTEM" "address" "TEXT" "NOSTEM"  "neighbourhood" "TAG" "SORTABLE" "description" "TEXT"  "building_type" "TEXT" "WEIGHT" "20" "NOSTEM" "SORTABLE"     "work_type" "TEXT" "NOSTEM" "SORTABLE"     "floor_area" "NUMERIC" "SORTABLE"     "construction_value" "NUMERIC" "SORTABLE"     "zoning" "TAG"     "units_added" "NUMERIC" "SORTABLE"     "location" "GEO"
    # ft.add testset 109056573-002 1 fields building_type "Retail and Shops" description "To change the use from a Restaurant to a Personal Service Shop (Great Clips)"
    # FT.SEARCH testset retail RETURN 1 description SUMMARIZE LIMIT 0 1
    self.cmd('ft.create', 'idx', 'SCHEMA', 'building_type', 'TEXT', 'description', 'TEXT')
    self.cmd('ft.add', 'idx', 'doc1', '1.0', 'FIELDS',
             'building_type', 'Retail and Shops',
             'description', 'To change the use from a Restaurant to a Personal Service Shop (Great Clips)')
    
    self.cmd('ft.add', 'idx', 'doc2', '1.0', 'FIELDS',
             'building_type', 'Retail and Shops',
             'description', 'To change the use from a Restaurant to a Personal Service Shop (Great Clips) at the end')

    ret = self.cmd('FT.SEARCH', 'idx', 'retail', 'RETURN', 1, 'description', 'SUMMARIZE')
    self.assertEqual([2L, 'doc2', ['description', 'To change the use from a Restaurant to a Personal Service Shop (Great Clips) at the'], 'doc1', ['description', 'To change the use from a Restaurant to a Personal Service Shop (Great Clips)']],
        ret)

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    from itertools import izip_longest
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)
