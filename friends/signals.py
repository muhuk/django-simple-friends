"""
Signals
=======

friendship_accepted
-------------------

.. data:: friends.signals.friendship_accepted

    Sent when a |FriendshipRequest| is accepted.

    Arguments sent with this signal:

    ``sender``
        |FriendshipRequest| instance that is accepted.


friendship_declined
-------------------

.. data:: friends.signals.friendship_declined

    Sent when a |FriendshipRequest| is declined by
    :attr:`~friends.models.FriendshipRequest.to_user`.

    Arguments sent with this signal:

    ``sender``
        |FriendshipRequest| instance that is declined.


friendship_cancelled
--------------------

.. data:: friends.signals.friendship_cancelled

    Sent when a |FriendshipRequest| is cancelled by
    :attr:`~friends.models.FriendshipRequest.from_user`.

    Arguments sent with this signal:

    ``sender``
        |FriendshipRequest| instance that is cancelled.


Signal Handlers
===============

.. automethod:: friends.signals.create_friendship_instance

.. automethod:: friends.signals.create_userblocks_instance
"""


from django.dispatch import Signal


friendship_accepted = Signal()


friendship_declined = Signal()


friendship_cancelled = Signal()


def create_friendship_instance(sender, instance, created, raw, **kwargs):
    """
    Create a |FriendshipRequest| for newly created |User|.

    .. seealso::
        :data:`~django.db.models.signals.post_save` built-in signal.
    """
    from friends.models import Friendship
    if created and not raw:
        Friendship.objects.create(user=instance)


def create_userblocks_instance(sender, instance, created, raw, **kwargs):
    """
    Create a |UserBlocks| for newly created |User|.

    .. seealso::
        :data:`~django.db.models.signals.post_save` built-in signal.
    """
    from friends.models import UserBlocks
    if created and not raw:
        UserBlocks.objects.create(user=instance)
