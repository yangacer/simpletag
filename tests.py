import unittest
import os
import anytag

class test_anytag(unittest.TestCase):

    def setUp(self):
        self.ns = anytag.ns('test', id_type=int)
        pass

    def tearDown(self):
        self.ns.purge()
        pass

    def test_create(self):
        ns_def = anytag.ns('tagDef')
        ns_int = anytag.ns('tagInt', id_type=int)
        ns_str = anytag.ns('tagStr', id_type=str)
        self.assertTrue(os.path.exists('tagDef'))
        self.assertTrue(os.path.exists('tagInt'))
        self.assertTrue(os.path.exists('tagStr'))
        anytag.purge('tagDef')
        anytag.purge('tagInt')
        anytag.purge('tagStr')
        pass

    def test_update_then_query_ids(self):
        self.ns.update(123, 'anytag is awsome!')
        self.ns.update(456, 'test is a MUST!')
        self.assertEqual([123, 456], self.ns.query_ids('is'))
        self.assertIn(456, self.ns.query_ids('is -awsome'))
        pass

    def test_update_then_query_tags(self):
        self.ns.update(123, 'anytag is awsome!')
        self.ns.update(456, 'test is a MUST!')
        self.assertEqual('anytag is awsome!', ' '.join(self.ns.query_tags(123)))
        self.assertEqual('test is a MUST!', ' '.join(self.ns.query_tags(456)))
        pass

    def test_stats(self):
        self.ns.update(123, 'anytag is awsome!')
        self.ns.update(456, 'test is a MUST!')
        stats = self.ns.stats()
        '''
        expected = dict(anytag=1,
                is=2,
                awsome=1,
                test=1,
                a=1,
                MUST=1)
        sefl.assertEqual(expected, stats)
        '''
        pass
