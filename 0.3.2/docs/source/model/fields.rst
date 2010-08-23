.. _model-field:

.. module:: stdnet.orm

============================
Scalar Fields
============================

The most important part of a model, and the only required part of a model,
is the list of database fields it defines. Fields are specified by class attributes.
They are the equivalent to django Fields and therefore
the equivalent of columns in a traditional relational databases.

.. _fieldbase:

Field Base Class
==============================

.. autoclass:: stdnet.orm.fields.Field
   :members:


.. _atomfield:

AtomField
==============================

.. autoclass:: stdnet.orm.fields.AtomField
   :members:


.. _autofield:
   
AutoField
==============================

.. autoclass:: stdnet.orm.fields.AutoField
   :members:
   
   
.. _datefield:
   
DateField
==============================

.. autoclass:: stdnet.orm.fields.DateField
   :members:
   

.. _foreignkey:
   
ForeignKey
==============================

.. autoclass:: stdnet.orm.fields.ForeignKey
   :members:
   
