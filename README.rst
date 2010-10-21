
:Documentation: http://packages.python.org/python-stdnet/
:Dowloads: http://pypi.python.org/pypi/python-stdnet/
:Source: http://code.google.com/p/python-stdnet/
:Keywords: server, database, cache, redis, orm

--

A networked standard template library for python.

The data is owned by different, configurable back-end databases and it is accessed using a
light-weight Object Relational Mapping (ORM_) inspired by Django_. 
The source code is hosted at `google code`__ while
Documentation__ and Downloads__ are available via PyPi.

__ http://code.google.com/p/python-stdnet/
__ http://packages.python.org/python-stdnet/
__ http://pypi.python.org/pypi/python-stdnet/


Backends
====================
Backend databases provide the backbone of the library, while the Object Relational Mapping
is the syntactic sugar. Currently the list of back-ends is limited to

* Redis_. Requires redis-py_.
* Local memory (planned). For testing purposes.
* CouchDB_ (planned). Requires couchdb-python_.
* Memcached_ (maybe).

Only Redis_ is fully operational.
 
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


Installing 
================================
To install, download, uncompress and type::

	python setup.py install

otherwise use ``easy_install``::

	easy_install python-stdnet
	
or ``pip``::

	pip install python-stdnet
	

Running Tests
======================
At the moment, only redis back-end is available, so to run tests you need to install redis.
Once done that, launch redis and type::

	>>> import stdnet
	>>> stdnet.runtests()
	
otherwise from the package directory::

	python runtests.py
	
Default settings
=========================
StdNet comes with few default settings. To run
tests with the above commands assume your Redis_ server
is running on the same machine. If this is not the case,
you need to setup a	script file along these lines::
	
	if __name__ == '__main__':
	    from stdnet.conf import settings
	    settings.DEFAULT_BACKEND = 'redis://your.server.url:6379/?db=10'
	    import stdnet
	    stdnet.runtests()


.. _Redis: http://code.google.com/p/redis/
.. _Django: http://www.djangoproject.com/
.. _redis-py: http://github.com/andymccurdy/redis-py
.. _ORM: http://en.wikipedia.org/wiki/Object-relational_mapping
.. _CouchDB: http://couchdb.apache.org/
.. _couchdb-python: http://code.google.com/p/couchdb-python/
.. _Memcached: http://memcached.org/
