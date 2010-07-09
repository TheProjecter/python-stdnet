
Python StdNet
=========================================

.. rubric:: A Networked Standard template library for Python.

An object relational mapper library for remote data-structures.
Simple to use and configure. Define your model::
	
	from stdnet import orm
	
	class TimeSerie(orm.StdModel):
	    ticker = orm.AtomField()
	    data   = orm.HashField()
		
register it to a backend::

	orm.register(TimeSerie,'redis://')
	
and create objects::

	ts = TimeSerie(ticker = 'GOOG').save()
	ts.data.add(date.today(),485)
	ts.save()


.. _contents:

Contents
------------

.. toctree::
   :maxdepth: 2
   
   model/index
   backends/index
   utility/index
   contrib/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

