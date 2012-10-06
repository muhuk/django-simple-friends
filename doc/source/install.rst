================================
Setting up django-simple-friends
================================

Installation
============

#. Install *django-simple-friends* package::

    pip install django-simple-friends

#. Add `friends` to your `INSTALLED_APPS` setting::

    INSTALLED_APPS = (
        # Other apps
        'friends',
    )

#. Run `syncdb` to create tables and seed friendship data for existing users::

    python manage.py syncdb

#. Run tests to make sure the app is installed correctly::

    python manage.py test friends

#. Optionally include `friends.urls` to your URLconf::

    urlpatterns = patterns('',
        # Other entries
        (r'^friends/', include('friends.urls')),
    )



Development Setup
=================

If you want to develop *django-simple-friends* you can follow the steps below to set up a development environment.

#. Log-in to your GitHub account and `fork <http://help.github.com/fork-a-repo/>`_ `the project <https://github.com/muhuk/django-simple-friends/>`_.

#. Create a virtual environment::

    virtualenv --no-site-packages django-simple-friends

#. Create a local repository::

    cd django-simple-friends
    . bin/activate
    git clone git@github.com:muhuk/django-simple-friends.git src

   .. warning::
       You need to replace `muhuk` with your GitHub username in the command above.

#. Run the tests to make sure everyting is set up correctly::

    cd src
    python example/manage.py test friends

#. Pick an `issue <https://github.com/muhuk/django-simple-friends/issues/>`_ to work on.
