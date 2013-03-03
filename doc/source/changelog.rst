=======
Changes
=======

Version 1.0.0 - In Development
==============================

* Some view classes are renamed::

      BaseFriendshipActionView  ->  BaseActionView
      FriendshipBlockView       ->  UserBlockView
      FriendshipUnblockView     ->  UserUnblockView

  If you are using only the view functions or the provided ``urls.py``, then
  you don't need to change your code.
* ``related_name``\ 's for the ``ForeignKey``\ 's to ``User`` from
  ``FriendshipRequest`` are changed as ``friendshiprequests_from`` and
  ``friendshiprequests_to``. Please replace any references to
  ``invitations_from`` and ``invitations_to`` in your code.


Version 0.5 - Oct 7, 2012
=========================

Tested with Django versions **1.3** & **1.4**.

* ``friend_list`` view is removed. See ``friends`` template filter.
* View functions are rewritten as class based views. But they still work as
  aliases.
* ``post_syncdb`` signals to fix the issue of ``User``\ s without
  ``Friendship``\ s.
* Proper Sphinx powered documentation.
* German & Spanish translations.


Version 0.4 - Feb 4, 2010
=========================

* Initial release.
