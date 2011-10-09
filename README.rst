**django-simple-friends** adds friendship management to your project.


Features
========

- Manages relationships between registered users only.
- Two phase friending.
- Blocking.


Installation
============

#. Add ``"django-simple-friends"`` directory to your Python path.
#. Add ``"friends"`` to your ``INSTALLED_APPS`` tuple found in
   your settings file.
#. Run ``syncdb`` to create tables and seed friendship data for existing users.
#. Include ``"friends.urls"`` to your URLconf. (optional)


Testing & Example
=================

You can use the project in the ``example`` directory in repository to run
tests::

    python example/manage.py test friends

Note that if you have installed **django-simple-friends** as a package you are
likely to have a project already, in this case you can just run the ``test``
command of your projects. Example project is intended for developers.


Usage
=====

TODO


See Also
========

-  `django-friends <http://github.com/jtauber/django-friends>`_

