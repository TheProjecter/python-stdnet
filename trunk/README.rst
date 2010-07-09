Python StdNet
===================

A networked standard template library for python. It includes a lightweight ORM inspired by Django__.
The source code is very much *alpha* and under continuous development.


Backends
====================

	* Redis__ (the real reason behind the development of this library)
	* Local memory (for testing and not fully supported)
	* Memcached__ (planned)
 
 
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
 		
	class Group(orm.StdModel):
		name = orm.AtomField(unique=True)

	class User(orm.StdModel):
		username = orm.AtomField(unique=True)
		password = orm.AtomField()
		group	 = orm.ForeignKey(Group)


__ http://code.google.com/p/redis/
__ http://memcached.org/
__ http://www.djangoproject.com/