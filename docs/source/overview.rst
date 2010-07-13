.. _intro-overview:

=====================
Overview
=====================

.. rubric:: A networked standard template library for python.

The data is owned by different, configurable back-end databases and it is accessed using a
light-weight Object Relational Mapping (ORM__) inspired by Django__. 
The source code is hosted at `google code <http://code.google.com/p/python-stdnet/>`_ while
Documentation__ and Downloads__ are
available via PyPi.

Backends
====================
Backend databases provide the backbone of the library, while the Object Relational Mapping
is the syntactic sugar. Currently the list of back-ends is limited to

 * Redis__. Requires redis-py__.
 * Local memory (planned). For testing purposes.
 * CouchDB__ (planned). Requires couchdb-python__.
 * Memcached__ (maybe)

Only Redis is fully operational.
 
 
Object-relational mapping
================================
The module ``stdnet.orm`` is a lightweight ORM. For example::
 
	from stdnet import orm
 		
	class Author(orm.StdModel):
	    name = orm.AtomField()

	class Book(orm.StdModel):
	    author = orm.ForeignKey(Author)
	    title  = orm.AtomField()
	    
Register models with backend::

	orm.register(Author,'redis://localhost/?db=1')
	orm.register(Book,'redis://localhost/?db=2')


Installing and Running
================================
To install::

	python setup.py install
	pip install python-stdnet
	easy_install python-stdnet
	
At the moment, only redis back-end is available, so to run tests you need to install redis. Once done that,
launch redis and type::

	python test.py	    
	    
__ http://en.wikipedia.org/wiki/Object-relational_mapping
__ http://www.djangoproject.com/
__ http://packages.python.org/python-stdnet/
__
__ http://code.google.com/p/redis/
__ http://github.com/andymccurdy/redis-py
__ http://couchdb.apache.org/
__ http://code.google.com/p/couchdb-python/
__ http://memcached.org/

