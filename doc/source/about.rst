===========================
About django-simple-friends
===========================

I started developing *django-simple-friends* when I needed a simple app that handles friendships for my project. `django-friends <https://github.com/jtauber/django-friends/>`_ of `Pinax <http://pinaxproject.com/>`_ was mature and well written but it was also handling contacts and invitations. So I decided to create my own app and steal some ideas from *django-friends*.

You can get community support at the |mailing-list|_.


Highlights
==========

- Only the relationships between registered users are managed.
- Friending with double confirmation. When a user adds another user as a friend, only when the other user accepts or tries to add the first user as a friend, the friendship relationship is created.
- Blocking is possible.

.. |mailing-list| replace:: mailing list
.. _mailing-list: https://groups.google.com/forum/?fromgroups=#!forum/django-simple-friends
