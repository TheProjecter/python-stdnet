Python StdNet
===================

A networked standard template library for python. It includes a lightweight ORM.


Backends
====================

 * local memory
 * memcached (not fully supported)
 * redis
 
 
 Installing and Running
 ================================
 To install::
 
 	python setup.py install
 	pip install python-stdnet
 	easy_install python-stdnet
 
 
 Object-relational mapping
 ================================
 The module ``stdnet.orm`` is a lightweight ORM.
 For example::
 
 	from stdnet import orm
 	
 	
 	class Group(orm.StdModel):
 		name = orm.AtomField(unique=True)
 		
 		
 	class User(orm.StdModel):
 		username = orm.AtomField(unique=True)
 		password = orm.AtomField()
 		group	 = orm.ForeignKey(Group)
 