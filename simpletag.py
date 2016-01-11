import sqlite3
import os

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

    SQL_CREATE_TBL = {
            int:  'CREATE VIRTUAL TABLE IF NOT EXISTS {} USING FTS4(tags);',
            str: 'CREATE VIRTUAL TABLE IF NOT EXISTS {} USING FTS4(docid_str, tags);'
            }
    SQL_CREATE_AUX_TBL =  'CREATE VIRTUAL TABLE IF NOT EXISTS {0}_terms USING fts4aux({0});'
    SQL_COL_INFO = 'PRAGMA table_info({});'
    SQL_PURGE_TBL = 'DELETE FROM {};'
    SQL_UPDATE = {
        int: 'INSERT OR REPLACE INTO {} (docid, tags) VALUES (?,?);',
        str: 'INSERT OR REPLACE INTO {} (docid_str, tags) VALUES (?, ?);',
        }
    SQL_QUERY_IDS = {
            int: 'SELECT docid FROM {} WHERE tags MATCH ?;',
            str: 'SELECT docid_str FROM {} WHERE tags MATCH ?;',
            }

    SQL_QUERY_TAGS = {
            int: 'SELECT tags FROM {} WHERE docid = ?;',
            str: 'SELECT tags FROM {} WHERE docid_str MATCH ?;',
            }
    SQL_STATS = {
        int: 'SELECT term, documents, occurrences FROM {}_terms WHERE col=0;',
        str: 'SELECT term, documents, occurrences FROM {}_terms WHERE col=1;',
    }
    pass


class ns(object):

    dbfile = 'simpletag.db'
    table = None
    id_type = None
    conn = None

    def __init__(self, name, id_type=int, conn=None):
        if id_type not in (int, str):
            raise TypeError('id_type is not supported')

        conn = sqlite3.connect(self.dbfile) if conn is None else conn
        conn.row_factory = sqlite3.Row
        csr = conn.cursor()
        sql = __CONSTS__.SQL_CREATE_TBL[id_type].format(name)
        csr.execute(sql)
        sql = __CONSTS__.SQL_CREATE_AUX_TBL.format(name)
        csr.execute(sql)
        conn.commit()
        sql = __CONSTS__.SQL_COL_INFO.format(name)
        csr.execute(sql)

        def is_mismatched(id_type, col_cnt):
            if col_cnt == 2 and id_type == str:
                return False
            if col_cnt == 1 and id_type == int:
                return False
            return True

        if is_mismatched(id_type, len(csr.fetchall())):
            raise TypeError('Redefine id_type')

        self.table = name
        self.id_type = id_type
        self.conn = conn
        pass

    def purge(self):
        csr = self.conn.cursor()
        csr.execute(__CONSTS__.SQL_PURGE_TBL.format(self.table))
        self.conn.commit()
        pass

    def update(self, ident, tag_str):
        if isinstance(ident, str) and self.id_type == int:
            raise TypeError('Mismatched doc id type')

        if not isinstance(tag_str, str) and not isinstance(tag_str, unicode):
            tag_str = ' '.join(tag_str)

        sql = __CONSTS__.SQL_UPDATE[self.id_type].format(self.table)
        csr = self.conn.cursor()
        csr.execute(sql, (ident, tag_str))
        self.conn.commit()
        pass

    def query_ids(self, query_str):
        sql = __CONSTS__.SQL_QUERY_IDS[self.id_type].format(self.table)
        csr = self.conn.cursor()
        for row in csr.execute(sql, (query_str,)):
            yield row[0]

    def query_tags(self, docid):
        sql = __CONSTS__.SQL_QUERY_TAGS[self.id_type].format(self.table)
        csr = self.conn.cursor()
        for row in csr.execute(sql, (docid,)):
            for tok in get_token(row[0]):
                yield tok

    def stats(self):
        sql = __CONSTS__.SQL_STATS[self.id_type].format(self.table)
        csr = self.conn.cursor()
        for row in csr.execute(sql):
            yield dict(((key, row[key]) for key in row.keys()))

