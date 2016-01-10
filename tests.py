# -*- coding: utf-8 -*-
import unittest
import os
import simpletag

class test_simpletag(unittest.TestCase):

    def setUp(self):
        self.ns = simpletag.ns('test', id_type=int)
        pass

    def tearDown(self):
        self.ns.purge()
        pass

    def test_update_str_then_query_ids(self):
        self.ns.update(123, 'simpletag is awsome!')
        self.ns.update(456, 'test is a MUST!')
        self.ns.update(789, u'中文 行不行')
        self.assertEqual([123, 456], self.ns.query_ids('is'))
        self.assertIn(456, self.ns.query_ids('is -awsome'))
        self.assertIn(789, self.ns.query_ids(u'行不行'))
        pass

    def test_update_list_then_query_ids(self):
        self.ns.update(123, ['simpletag', 'is', 'awsome'])
        self.ns.update(456, ['test', 'is', 'a', 'MUST'])
        self.ns.update(789, [u'中文', u'行不行'])
        self.assertEqual([123, 456], self.ns.query_ids('is'))
        self.assertIn(456, self.ns.query_ids('is -awsome'))
        self.assertIn(789, self.ns.query_ids(u'行不行'))
        pass

    def test_update_then_query_tags(self):
        self.ns.update(123, 'simpletag is awsome!')
        self.ns.update(456, 'test is a MUST!')
        self.ns.update(789, u'中文 行不行')
        self.assertEqual(['simpletag', 'is', 'awsome'], self.ns.query_tags(123))
        self.assertEqual(['test', 'is', 'a', 'MUST'], self.ns.query_tags(456))
        self.assertEqual([u'中文', u'行不行'], self.ns.query_tags(789))
        pass

    def test_stats(self):
        self.ns.update(123, 'simpletag is awsome!')
        self.ns.update(456, 'test is a MUST!')
        stats = self.ns.stats()
        '''
        expected = dict(simpletag=1,
                is=2,
                awsome=1,
                test=1,
                a=1,
                MUST=1)
        sefl.assertEqual(expected, stats)
        '''
        pass
