# -*- coding: utf-8 -*-
import unittest
import os
import simpletag

class test_simpletag(unittest.TestCase):

    SQLITE_COMPILE_OPTS = []

    @classmethod
    def setUpClass(cls):
        import sqlite3
        print '===='
        print 'sqlite ver', sqlite3.sqlite_version
        print '===='
        pass

    def setUp(self):
        self.ns = simpletag.IntNS('test')
        self.ns_str = simpletag.TextNS('test_str')
        pass

    def tearDown(self):
        self.ns.purge()
        self.ns_str.purge()
        pass

    def test_invalid_init(self):

        with self.assertRaises(NotImplementedError):
            simpletag.ns()

        pass

    def test_open_failure(self):

        with self.assertRaises(TypeError):
            simpletag.TextNS('test')

        with self.assertRaises(TypeError):
            simpletag.IntNS('test_str')
        pass

    def test_update_failure(self):

        with self.assertRaises(TypeError):
            self.ns.update('invalid', 'noop')

        with self.assertRaises(TypeError):
            self.ns_str.update(1, 'noop')

        pass

    def test_update_str_then_query_ids(self):
        self.ns.update(123, 'simpletag is awsome!')
        self.ns.update(456, 'test is a MUST!')
        self.ns.update(789, u'中文 行不行')
        self.assertEqual([123, 456], [i for i in self.ns.query_ids('is')])
        self.assertIn(789, [i for i in self.ns.query_ids(u'行不行')])
        pass

    def test_update_list_then_query_ids(self):
        self.ns.update(123, ['simpletag', 'is', 'awsome'])
        self.ns.update(456, ['test', 'is', 'a', 'MUST'])
        self.ns.update(789, [u'中文', u'行不行'])
        self.assertEqual([123, 456], [i for i in self.ns.query_ids('is')])
        self.assertIn(789, [i for i in self.ns.query_ids(u'行不行')])

    def test_update_list_then_query_str_ids(self):
        self.ns_str.update('/a/b', ['simpletag', 'is', 'awsome'])
        self.ns_str.update('/', ['test', 'is', 'a', 'MUST'])
        self.ns_str.update('/b/a', [u'中文', u'行不行'])
        self.assertEqual(['/a/b', '/'], [i for i in self.ns_str.query_ids('is')])
        self.assertIn('/b/a', [i for i in self.ns_str.query_ids(u'行不行')])
        pass

    def test_set_query(self):
        self.ns.update(123, ['simpletag', 'is', 'awsome'])
        self.ns.update(456, ['test', 'is', 'a', 'MUST'])

        query = None
        if self.ns.using_parenthesis_query:
            query = 'is NOT awsome'
        else:
            query = 'is -awsome'

        self.assertIn(456, [i for i in self.ns.query_ids(query)])
        pass

    def test_update_then_query_tags(self):
        self.ns.update(123, 'simpletag is awsome!')
        self.ns.update(456, 'test is a MUST!')
        self.ns.update(789, u'中文 行不行')
        self.assertEqual(['simpletag', 'is', 'awsome'], [i for i in self.ns.query_tags(123)])
        self.assertEqual(['test', 'is', 'a', 'MUST'], [i for i in self.ns.query_tags(456)])
        self.assertEqual([u'中文', u'行不行'], [i for i in self.ns.query_tags(789)])
        pass

    def test_stats(self):
        self.ns.update(123, 'simpletag is awsome!')
        self.ns.update(456, 'test is a MUST!')
        self.ns.update(789, u'中文 行不行 中文')
        expected = [
                dict(term='a',          documents=1, occurrences=1),
                dict(term='awsome',     documents=1, occurrences=1),
                dict(term='is',         documents=2, occurrences=2),
                dict(term='must',       documents=1, occurrences=1),
                dict(term='simpletag',  documents=1, occurrences=1),
                dict(term='test',       documents=1, occurrences=1),
                dict(term=u'中文',      documents=1, occurrences=2),
                dict(term=u'行不行',    documents=1, occurrences=1),
                ]
        self.assertEqual(expected, [st for st in self.ns.stats()])
        pass

    def test_str_stats(self):
        self.ns_str.update('/test-str/123', 'nothing')
        expected = [
                dict(term='nothing', documents=1, occurrences=1),
        ]
        self.assertEqual(expected, [st for st in self.ns_str.stats()])
        pass
