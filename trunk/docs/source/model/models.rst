.. _model-model:

============================
StdNet Models
============================

A model is the single, definitive source of data about your data.
It contains the essential fields and behaviors of the data you’re storing.
Each model maps to a single database table.

Defining a stdnet models is simple, you derive a Python class from ``StdModel``::

	from stdnet import orm
	
	class Author(orm.StModel):
	    name = orm.AtomField()
	
	class Book(orm.StdModel):
	    title  = orm.AtomField()
	    author = orm.ForeignKey(Author)
	    
	    
	    
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

 