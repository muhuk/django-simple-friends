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

Usage examples.

First, we're going to get two different users for our examples::

     user1 = User.objects.get(id=1)
     user2 = User.objects.get(id=2)

Friend request
--------------

``user1`` requests friendship to ``user2``::

     FriendshipRequest.objects.create(from_user=user1, to_user=user2, message='Friends?')

Accepting friendship request
----------------------------

``user2`` accepts ``user1`` request::

    fr = FriendshipRequest.objects.get(from_user=user1, to_user=user2, accepted=False)
    fr.accept()

Declining friendship request
----------------------------

``user2`` declines ``user1`` request::

    fr = FriendshipRequest.objects.get(from_user=user1, to_user=user2, accepted=False)
    fr.decline()


Are we friends?
---------------

If users are friends then return ``True``::

    Friendship.objects.are_friends(user1, user2):

Getting all friends of a user
-----------------------------

``friends`` will be a list with all id's from ``user1`` friends::

    friends = Friendship.objects.friends_of(user1).values_list('id', flat=True)


See Also
========

-  `django-friends <http://github.com/jtauber/django-friends>`_
