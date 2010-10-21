.. _model-model:

.. module:: stdnet.orm.models

============================
StdNet Models
============================

The StdNet Object Relational Mapper presents a method of
associating user-defined Python classes with
a database :ref:`backends <backends>` data. These python classes
are referred as **models** and are subclasses of
:class:`stdnet.orm.StdModel`.

.. autoclass:: stdnet.orm.StdModel
   :members:


.. _creating-models:

Creating Models
======================

Defining a stdnet models is simple, you derive a Python class from ``StdModel``::

	from stdnet import orm
	
	class Author(orm.StModel):
	    name = orm.AtomField()
	
	class Book(orm.StdModel):
	    title  = orm.AtomField()
	    author = orm.ForeignKey(Author, related_name = 'books')
	    
	    
.. _register-model:
	    
Register A Model
=====================

Once a model is defined, in order to use it in an application it needs to be registered with
a back-end database.

For Redis the syntax is the following::

	import orm
	
	orm.register(Author, 'redis://my.host.name:6379/?db=1')
	orm.register(Book, 'redis://my.host.name:6379/?db=2')
	
``my.host.name`` can be ``localhost`` or an ip address while ``db`` indicate
the database number (very useful for separating data on the same redis instance).

 
.. _database-metaclass:

Database Metaclass
==========================

.. autoclass:: stdnet.orm.base.Metaclass
   :members: