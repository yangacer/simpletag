# SimpleTag

[![Build Status](https://travis-ci.org/yangacer/simpletag.svg?branch=master)](https://travis-ci.org/yangacer/simpletag)
[![Coverage Status](https://coveralls.io/repos/yangacer/simpletag/badge.svg?branch=master&service=github)](https://coveralls.io/github/yangacer/simpletag?branch=master)
[![PyPi](https://img.shields.io/pypi/v/simpletag.svg)](https://pypi.python.org/pypi/simpletag)

## Source

https://github.com/yangacer/simpletag

## Usage

```
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
```

## TODOs

- As a Flask plug-in
- Benchmark
- Further tags analytics (e.g. top-k ~ KNN classification)

