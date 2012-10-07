=======
Changes
=======

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
