===========================
About django-simple-friends
===========================

I started developing *django-simple-friends* when I needed a simple app that handles friendships for my project. `django-friends <https://github.com/jtauber/django-friends/>`_ of `Pinax <http://pinaxproject.com/>`_ was mature and well written but it was also handling contacts and invitations. So I decided to create my own app and steal some ideas from *django-friends*.


Highlights
==========

- Only the relationships between registered users are managed.
- Friending with double confirmation. When a user adds another user as a friend, only when the other user accepts or tries to add the first user as a friend, the friendship relationship is created.
- Blocking is possible.
