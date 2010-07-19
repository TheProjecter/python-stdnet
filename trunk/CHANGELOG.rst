python-stdnet 0.3.1 
========================================
 * Bug fixes.
 * 27 tests.

python-stdnet 0.3.0 - 2010 July 15
========================================
 * Overall code refactoring.
 * Added ListField and OrderedSetField with Redis implementation.
 * StdModel raise AttributError when method/attribute not available. Previously it returned None.
 * StdModel raise ModelNotRegistered when trying to save an instance of a non-registered model.
 * 24 tests.

python-stdnet 0.2.2 - 2010 July 7
========================================
 * RelatedManager is derived by Manager and therefore implements both all and filter methods.
 * 10 tests

python-stdnet 0.2.0  - 2010 June 21
========================================
 * First official release in pre-alpha
 * Redis Backend
 * Initial ORM with AtomField, DateField and ForeignKey.
 * 8 tests