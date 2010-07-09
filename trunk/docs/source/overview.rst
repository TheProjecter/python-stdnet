.. _intro-overview:

Python StdNet Overview
=========================

A networked standard template library for python.
It includes a light weight ORM inspired by Django__.
The source code is hosted at `google code <http://code.google.com/p/python-stdnet/>`_ 
and it is under continuous development.

Backends
====================
 * Redis__. Requires redis-py__.
 * Local memory (planned). For testing purposes.
 * CouchDB__ (planned). Requires couchdb-python__.
 * Memcached__ (maybe)
 
 
Installing and Running
================================
To install::

	python setup.py install
	pip install python-stdnet
	easy_install python-stdnet
	
At the moment, only redis back-end is available, so to run tests you need to install redis. Once done that,
launch redis and type::

	python test.py
 
 
Object-relational mapping
================================
The module ``stdnet.orm`` is a lightweight ORM. For example::
 
	from stdnet import orm
 		
	class Author(orm.StdModel):
	    name = orm.AtomField()

	class Book(orm.StdModel):
	    author = orm.ForeignKey(Author)
	    title  = orm.AtomField()
	    
	    
__ http://www.djangoproject.com/
__ http://code.google.com/p/redis/
__ http://github.com/andymccurdy/redis-py
__ http://couchdb.apache.org/
__ http://code.google.com/p/couchdb-python/
__ http://memcached.org/

