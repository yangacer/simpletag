# -*- coding: utf-8 -*-
import sqlite3

__author__ = 'Acer.Yang <yangacer@gmail.com>'
__version__ = '0.1.5'


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
            '''
        )

        self.open_table_(name)
        pass

    def update(self, ident, tags):
        if not isinstance(ident, str):
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
            CREATE VIRTUAL TABLE IF NOT EXISTS {0} USING FTS4(tags);
            CREATE VIRTUAL TABLE IF NOT EXISTS {0}_terms USING fts4aux({0});
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
