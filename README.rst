SimpleTag
=========

|Build Status| |Coverage Status| |PyPi|

Source
------

https://github.com/yangacer/simpletag

Usage
-----

::

    >>> import simpletag

    >>> ns = simpletag.TextNS('myTextTagSpace') # Create a namespace of text IDs
    ... # Create integer IDs namespace with `simpletag.IntNS()`

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

    >>> print [ st for st in ns.stats() ]
    [{
        'term': u'simple', 'documents': 1, 'occurrences': 1
    }, {
        'term': u'tag', 'documents': 2, 'occurrences': 2
    }]

    >>> ns.purge()

Tag Query
---------

Tag set query with SQLite FTS query syntax.

::

    >>> ns.update(1, [u'民主', u'自由'])
    >>> ns.update(2, [u'民主', u'Cxin123'])

    >>> query  = ''
    ... # Query IDs of tags '民主' but not 'Cxin*' (tags start with Cxin)

    >>> if ns.using_parenthesis_query:
    >>>     query = u'民主 NOT Cxin*'
    >>> else:
    >>>     query = u'民主 -Cxin*'

    >>> print [tag for tag in ns.query_ids(query)]
    [1]

| **NOTE** SQLite supports ``standard`` and ``parenthesis`` syntax, and
  the two are enabled mutual exclusively at compiling SQLite. Detect which one
  being used thru ``simpletag.ns.using_parenthesis``. See `SQLite
  documentation <http://www.sqlite.org/fts3.html#section_3>`__ for
  further information.

TODOs
-----

-  As a Flask plug-in
-  Benchmark
-  Further tags analytics (e.g. top-k ~ KNN classification)

.. |Build Status| image:: https://travis-ci.org/yangacer/simpletag.svg?branch=master
   :target: https://travis-ci.org/yangacer/simpletag
.. |Coverage Status| image:: https://coveralls.io/repos/yangacer/simpletag/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/yangacer/simpletag?branch=master
.. |PyPi| image:: https://img.shields.io/pypi/v/simpletag.svg
   :target: https://pypi.python.org/pypi/simpletag
