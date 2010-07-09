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