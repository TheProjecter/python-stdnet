.. _model-field-structure:

.. module:: stdnet.orm

============================
Data-structure Fields
============================

These fields are remote data-structures such as list, sets and hash tables.
They can be bound to models so that
many-to-many objects relationship can be established. All the data-structure
fields derives from MultiField.

.. autoclass:: stdnet.orm.std.MultiField
   :members:



.. _listfield:

ListField
==============================

.. autoclass:: stdnet.orm.std.ListField
   :members:
   
   
.. _setfield:

SetField
==============================

.. autoclass:: stdnet.orm.std.SetField
   :members:
   
.. _orderedsetfield:

OrederedSetField
==============================

.. autoclass:: stdnet.orm.std.OrderedSetField
   :members:
   
   
.. _hashfield:

HashField
==============================

.. autoclass:: stdnet.orm.std.HashField
   :members:


.. _manytomanyfield:

ManyToManyField
==============================

.. autoclass:: stdnet.orm.std.ManyToManyField
   :members:

   