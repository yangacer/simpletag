# -*- coding: utf-8 -*-
import math
import sqlite3

__author__ = 'Acer.Yang <yangacer@gmail.com>'
__version__ = '0.1.7'


def get_token(text):
    out = ''
    for c in text:
        if c.isalnum() or ord(c) >= 128:
            out += c
        elif len(out):
            yield out
            out = ''
    if len(out):
        yield out
    pass


class __CONSTS__(object):

    SQL_COL_INFO = 'PRAGMA table_info({});'
    SQL_PURGE_TBL = 'DELETE FROM {};'
    SQL_STATS = '''
    SELECT term, documents, occurrences FROM {}_terms WHERE col=0;
    '''
    pass


class ns(object):

    dbfile = 'simpletag.db'
    table = None
    conn = None
    using_parenthesis_query = False

    def resolve_supported_level(self):
        sql = 'PRAGMA compile_options;'
        csr = self.conn.cursor()
        opts = [row[0] for row in csr.execute(sql)]
        if 'ENABLE_FTS3' not in opts:
            raise RuntimeError('SQLite''s FTS is not enabled')
        if 'ENABLE_FTS3_PARENTHESIS' in opts:
            self.using_parenthesis_query = True
        pass

    def get_existing_tbl_type(self, name):
        sql = 'select name from sqlite_master where type = "table";'
        csr = self.conn.cursor()
        return [row[0] for row in csr.execute(sql)]

    def __init__(self):
        raise NotImplementedError()

    def __priv_init__(self):
        conn = sqlite3.connect(self.dbfile)
        conn.row_factory = sqlite3.Row
        self.conn = conn
        self.resolve_supported_level()
        self.conn.create_aggregate('mad', 1, mad)
        self.conn.create_aggregate('stdev', 1, stdev)
        self.conn.create_function('tuple_n', 2, tuple_n)
        pass

    def open_table_(self, name):
        csr = self.conn.cursor()
        sql = self.__sql__['SQL_CREATE_TBL'].format(name)
        csr.executescript(sql)
        self.conn.commit()
        for k, v in self.__sql__.iteritems():
            self.__sql__[k] = v.format(name)
        self.table = name
        pass

    def purge(self):
        csr = self.conn.cursor()
        csr.execute(__CONSTS__.SQL_PURGE_TBL.format(self.table))
        self.conn.commit()
        pass

    def query_ids(self, query_str):
        sql = self.__sql__['SQL_QUERY_IDS']
        csr = self.conn.cursor()
        for row in csr.execute(sql, (query_str,)):
            yield row[0]

    def query_by_tags(self, query_str, tokenize=True):
        sql = self.__sql__['SQL_QUERY_BY_TAGS']
        csr = self.conn.cursor()
        for row in csr.execute(sql, (query_str, )):
            if tokenize is True:
                yield row[0], [tok for tok in get_token(row[1])]
            else:
                yield row[0], row[1]

    def query_tags(self, docid):
        sql = self.__sql__['SQL_QUERY_TAGS']
        csr = self.conn.cursor()
        for row in csr.execute(sql, (docid,)):
            for tok in get_token(row[0]):
                yield tok

    def stats(self):
        csr = self.conn.cursor()
        for row in csr.execute(__CONSTS__.SQL_STATS.format(self.table)):
            yield dict(((key, row[key]) for key in row.keys()))
            pass
        pass

    def build_weight(self):
        csr_term = self.conn.cursor()
        csr_docs = self.conn.cursor()
        csr_modify = self.conn.cursor()
        total_doc_num = 0

        sql_sel_docnum = 'SELECT value FROM {}_stat'.format(self.table)
        sql_sel_stat = __CONSTS__.SQL_STATS.format(self.table)
        sql_sel_docsize = 'SELECT * from {}_docsize'.format(self.table)

        for row in csr_term.execute(sql_sel_docnum):
            _, total_doc_num = decode_fts_varint(row[0])

        lg2_total_doc_num = math.log(total_doc_num, 2)

        csr_modify.execute('DELETE FROM {}_weight'.format(self.table))

        for term_rec in csr_term.execute(sql_sel_stat):

            for doc_rec in csr_docs.execute(sql_sel_docsize):
                _, doc_len = decode_fts_varint(doc_rec[1])
                weight = (
                    lg2_total_doc_num - math.log(term_rec[2], 2)
                ) / math.sqrt(doc_len)
                csr_modify.execute(
                    self.__sql__['SQL_INSERT_WEIGHT'],
                    (term_rec[0], doc_rec[0], weight)
                )
            pass
        self.conn.commit()
        pass

    def build_balltree(self):
        csr = self.conn.cursor()
        sql = '''
        SELECT term,
            CAST (tuple_n(med_div, 0) AS REAL) median
        FROM (
            SELECT term, mad(weight) med_div
            FROM {}_weight GROUP BY term
        ) ORDER BY CAST (tuple_n(med_div, 1) AS REAL)
        '''.format(self.table)

        for row in csr.execute(sql):
            print row
            pass

    pass


def tuple_n(tup, n):
    return tup.split()[int(n)]

class mad:

    def __init__(self):
        self.arr = []

    def step(self, value):
        self.arr.append(value)

    def _med_aux(self):
        l = len(self.arr)
        return (self.arr[(l - 1)/2] + self.arr[l/2]) / 2.0

    def finalize(self):
        arr_len = len(self.arr)
        self.arr.sort()
        med = self._med_aux()
        self.arr[:] = map(lambda v: v - med, self.arr)
        self.arr.sort()
        # print self.arr
        return '{} {}'.format(
            med,
            self.arr[len(self.arr)/2]
        )


class stdev:
    def __init__(self):
        self.arr = []
        self.total = 0

    def step(self, value):
        self.total += value
        self.arr.append(value * value)

    def finalize(self):
        avg = self.total / len(self.arr)
        return reduce(lambda s, v: math.pow(v - avg, 2), self.arr, 0)

def decode_fts_varint(blob):
    r'''
    Decode 1 varint and return used bytes and decoded value.

    >>> blob = b'\x7f\x81\x00'
    >>> decode_fts_varint(blob)
    (1, 127)

    >>> decode_fts_varint(blob[1:])
    (2, 128)
    '''
    used = 0
    result = 0
    for b in blob:
        b = ord(b)
        result <<= 7
        result |= b & ~0x80
        used += 1
        if 0 == b & 0x80:
            break
        pass
    return used, result


class TextNS(ns):
    """
    >>> import simpletag

    >>> ns = simpletag.TextNS('myTextTagSpace')

    >>> doc_1 = '/a/b'
    >>> tags_1 = ['tag']

    >>> doc_2 = '/b/a'
    >>> tags_2 = 'tag simple!'

    >>> ns.update(doc_1, tags_1)
    >>> ns.update(doc_2, tags_2)

    >>> print [ doc for doc in ns.query_ids('tag') ]
    [u'/a/b', u'/b/a']

    >>> print [ tag for tag in ns.query_tags(doc_1) ]
    [u'tag']

    >>> print [ st for st in ns.stats() ] # doctest: +NORMALIZE_WHITESPACE
    [{'term': u'simple', 'documents': 1, 'occurrences': 1},
            {'term': u'tag', 'documents': 2, 'occurrences': 2}]

    >>> ns.purge()
    """

    def __init__(self, name):

        super(TextNS, self).__priv_init__()
        tbls = self.get_existing_tbl_type(name)
        if name in tbls and (name + '_text_id') not in tbls:
            raise TypeError(name)

        self.__sql__ = dict(
            SQL_CREATE_TBL='''
            PRAGMA journal_mode=WAL;
            PRAGMA recursive_triggers='ON';
            CREATE VIRTUAL TABLE IF NOT EXISTS {0} USING FTS4(tags);
            CREATE TABLE IF NOT EXISTS {0}_text_id (
                textid TEXT UNIQUE PRIMARY KEY NOT NULL);
            CREATE VIRTUAL TABLE IF NOT EXISTS {0}_terms USING fts4aux({0});
            CREATE TRIGGER IF NOT EXISTS {0}_del_text_id
                AFTER DELETE ON {0}_text_id
                BEGIN
                    DELETE FROM {0} WHERE docid=OLD.rowid;
                END;
            CREATE TABLE IF NOT EXISTS {0}_weight (
                term TEXT NOT NULL,
                docid TEXT NOT NULL,
                weight INTEGER NOT NULL);
            ''',
            SQL_INSERT='INSERT OR REPLACE INTO {}_text_id VALUES(?);',
            SQL_UPDATE_1='DELETE FROM {} WHERE docid=?;',
            SQL_UPDATE_2='INSERT INTO {} (docid, tags) VALUES (?, ?);',
            SQL_PURGE_TBL='DELETE FROM {0}; DELETE FROM {0}_text_id;',
            SQL_DEL='''
            DELETE FROM {0} WHERE docid=(
                SELECT rowid FROM {0}_text_id WHERE textid=?);
            ''',
            SQL_QUERY_IDS='''
            SELECT * FROM {0}_text_id AS lhs
                JOIN (SELECT docid FROM {0} WHERE tags MATCH ?) AS rhs
                ON (lhs.rowid=rhs.docid);
            ''',
            SQL_QUERY_BY_TAGS='''
            SELECT * FROM {0}_text_id, {0} WHERE {0}.tags MATCH ? AND
                {0}_text_id.rowid = {0}.docid;
            ''',
            SQL_QUERY_TAGS='''
            SELECT tags FROM {0} WHERE docid=(
                SELECT rowid FROM {0}_text_id WHERE textid=?);
            ''',
            SQL_STATS='''
            SELECT term, documents, occurrences FROM {}_terms WHERE col=0;
            ''',
            SQL_INSERT_WEIGHT='''
            INSERT INTO {0}_weight VALUES (?,
                (SELECT textid from {0}_text_id WHERE rowid = ?),
            ?)
            '''
        )

        self.open_table_(name)
        pass

    def update(self, ident, tags):
        if not isinstance(ident, str) and not isinstance(ident, unicode):
            raise TypeError('Invalid ident type')

        if not isinstance(tags, str) and not isinstance(tags, unicode):
            tags = ' '.join(tags)

        csr = self.conn.cursor()
        sql = self.__sql__['SQL_INSERT']
        csr.execute(sql, (ident, ))

        rowid = csr.lastrowid
        sql = self.__sql__['SQL_UPDATE_1']
        csr.execute(sql, (rowid, ))

        sql = self.__sql__['SQL_UPDATE_2']
        csr.execute(sql, (rowid, tags))
        self.conn.commit()
        pass

    pass


class IntNS(ns):
    """
    >>> import simpletag

    >>> ns = simpletag.IntNS('myIntTagSpace')

    >>> doc_1 = 1
    >>> tags_1 = ['tag']

    >>> doc_2 = 2
    >>> tags_2 = 'tag simple!'

    >>> ns.update(doc_1, tags_1)
    >>> ns.update(doc_2, tags_2)

    >>> print [ doc for doc in ns.query_ids('tag') ]
    [1, 2]

    >>> print [ tag for tag in ns.query_tags(doc_1) ]
    [u'tag']

    >>> print [ st for st in ns.stats() ] # doctest: +NORMALIZE_WHITESPACE
    [{'term': u'simple', 'documents': 1, 'occurrences': 1},
            {'term': u'tag', 'documents': 2, 'occurrences': 2}]

    >>> ns.purge()
    """

    def __init__(self, name, conn=None):

        super(IntNS, self).__priv_init__()
        tbls = self.get_existing_tbl_type(name)
        if name in tbls and (name + '_text_id') in tbls:
            raise TypeError(name)

        self.__sql__ = dict(
            SQL_CREATE_TBL='''
            PRAGMA journal_mode=WAL;
            CREATE VIRTUAL TABLE IF NOT EXISTS {0} USING FTS4(tags);
            CREATE VIRTUAL TABLE IF NOT EXISTS {0}_terms USING fts4aux({0});
            CREATE TABLE IF NOT EXISTS {0}_weight (
                term TEXT NOT NULL,
                docid TEXT NOT NULL,
                weight INTEGER NOT NULL);
            ''',
            SQL_UPDATE_1='DELETE FROM {} WHERE docid=?;',
            SQL_UPDATE_2='INSERT INTO {} (docid, tags) VALUES (?, ?);',
            SQL_PURGE_TBL='DELETE FROM {0};',
            SQL_DEL='DELETE FROM {} WHERE docid=?;',
            SQL_QUERY_IDS='SELECT docid FROM {0} WHERE tags MATCH ?;',
            SQL_QUERY_BY_TAGS='''
            SELECT docid, tags FROM {0} WHERE tags MATCH ?;
            ''',
            SQL_QUERY_TAGS='SELECT tags FROM {} WHERE docid=?;',
            SQL_STATS='''
            SELECT term, documents, occurrences FROM {}_terms WHERE col=0;
            ''',
            SQL_INSERT_WEIGHT='INSERT INTO {0}_weight VALUES (?, ?, ?)',
        )

        self.open_table_(name)
        pass

    def update(self, ident, tags):
        if not isinstance(ident, int):
            raise TypeError('Invalid ident type')

        if not isinstance(tags, str) and not isinstance(tags, unicode):
            tags = ' '.join(tags)

        csr = self.conn.cursor()

        sql = self.__sql__['SQL_UPDATE_1']
        csr.execute(sql, (ident, ))

        sql = self.__sql__['SQL_UPDATE_2']
        csr.execute(sql, (ident, tags))
        self.conn.commit()
        pass

    pass
