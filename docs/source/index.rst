.. Python StdNet documentation master file, created by
   sphinx-quickstart on Thu Jun 17 11:24:36 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python StdNet
=========================================

.. rubric:: A Networked Standard template library for Python.

Define your model::
	
	from stdnet import orm
	
	class TimeSerie(orm.StdModel):
		ticker = orm.AtomField()
		data   = orm.HashField()
		
Register your model to a backend::

	orm.register(TimeSerie,'redis://')
	
Django style object::

	ts = TimeSerie(ticker = 'GOOG').save()
	ts.data.add(date.today(),485)
	ts.save()

Contents:

.. toctree::
   :maxdepth: 2
   
   model/index
   utility/index
   contrib/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

