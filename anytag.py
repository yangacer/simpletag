import sqlite3
import os

class __CONSTS__(object):

    SQL_CREATE_TBL = {
            int:  'CREATE VIRTUAL TABLE IF NOT EXISTS {} USING FTS4(tags);',
            str: 'CREATE VIRTUAL TABLE IF NOT EXISTS {} USING FTS4(docid_str, tags);'
            }
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
            str: 'SELECT tags FROM {} WHERE docid_str = ?;',
            }
    pass

def purge(name):
    os.remove(name)

class ns(object):

    dbfile = 'anytag.db'
    table = None
    id_type = None
    conn = None

    def __init__(self, name, id_type=int, conn=None):
        if id_type not in (int, str):
            raise TypeError('id_type is not supported')

        conn = sqlite3.connect(self.dbfile) if conn is None else conn
        csr = conn.cursor()
        sql = __CONSTS__.SQL_CREATE_TBL[id_type].format(name)
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
        sql = __CONSTS__.SQL_UPDATE[self.id_type].format(self.table)
        csr = self.conn.cursor()
        csr.execute(sql, (ident, tag_str))
        self.conn.commit()
        pass

    def query_ids(self, query_str):
        sql = __CONSTS__.SQL_QUERY_IDS[self.id_type].format(self.table)
        csr = self.conn.cursor()
        def gen():
            for row in csr.execute(sql, (query_str,)):
                yield row[0]
        return [docid for docid in gen()]

    def query_tags(self, docid):
        sql = __CONSTS__.SQL_QUERY_TAGS[self.id_type].format(self.table)
        csr = self.conn.cursor()
        def gen():
            for row in csr.execute(sql, (docid,)):
                yield row[0]
        return [tag for tag in gen()]

    def stats(self):
        pass

