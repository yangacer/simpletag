# SimpleTag

[![Build Status](https://travis-ci.org/yangacer/simpletag.svg?branch=master)](https://travis-ci.org/yangacer/simpletag)
[![Coverage Status](https://coveralls.io/repos/yangacer/simpletag/badge.svg?branch=master&service=github)](https://coveralls.io/github/yangacer/simpletag?branch=master)

## Usage

```
>>> import simpletag

>>> ns = simpletag.ns('myTagSpace', id_type=str)

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

>>> print [ st for st in ns.stats() ]
[{'term': u'simple', 'documents': 1, 'occurrences': 1}, {'term': u'tag', 'documents': 2, 'occurrences': 2}]

```

## Planned Features

- As a Flask plug-in
