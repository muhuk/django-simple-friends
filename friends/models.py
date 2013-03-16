"""
Models
======

.. autoclass:: FriendshipRequest
    :members:

.. autoclass:: FriendshipManager
    :members:

.. autoclass:: Friendship
    :members:

.. autoclass:: UserBlocks
    :members:

.. |bool| replace:: :func:`bool <bool>`
.. |int| replace:: :func:`int <int>`
.. |ManyToManyField| replace:: :class:`~django.db.models.ManyToManyField`
.. |OneToOneField| replace:: :class:`~django.db.models.OneToOneField`
.. |User| replace:: :class:`~django.contrib.auth.models.User`
.. |unicode| replace:: :func:`unicode <unicode>`
"""


import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import signals


class FriendshipRequest(models.Model):
    """
    An intent to create a friendship between two users.

    .. seealso::

        There should never be complementary :class:`FriendshipRequest`\ 's,
        as in ``user1`` requests to be friends with ``user2`` when ``user2``
        has been requested to be friends with ``user1``. See how
        :class:`~friends.views.FriendshipRequestView` checks the existence of
        a :class:`FriendshipRequest` from ``to_user`` to ``from_user``.
    """

    from_user = models.ForeignKey(User, related_name="friendshiprequests_from")
    """
    :class:`~django.db.models.ForeignKey` to |User| who initiated the request.
    """

    to_user = models.ForeignKey(User, related_name="friendshiprequests_to")
    """
    :class:`~django.db.models.ForeignKey` to |User| the request has been sent.
    """

    message = models.CharField(max_length=200, blank=True)
    """
    :class:`~django.db.models.CharField` containing the optional message.

    .. note::

        ``__unicode__()`` method of this class **does not** print out this
        field. You must explicitly access this field to output the message.

    Although :mod:`django-simple-friends <friends>` doesn't provide any
    functionality to use markup engines to render this message it doesn't
    prevent you to store and render it in any format you desire.
    """

    created = models.DateTimeField(default=datetime.datetime.now,
                                   editable=False)
    """
    :class:`~django.db.models.DateTimeField` set when the object is created.
    """

    accepted = models.BooleanField(default=False)
    """
    :class:`~django.db.models.BooleanField` indicates whether the request is
    accepted or still pending.
    """

    class Meta:
        verbose_name = _(u'friendship request')
        verbose_name_plural = _(u'friendship requests')
        unique_together = (('to_user', 'from_user'),)

    def __unicode__(self):
        return _(u'%(from_user)s wants to be friends with %(to_user)s') % {
            'from_user': unicode(self.from_user),
            'to_user': unicode(self.to_user),
        }

    def accept(self):
        """
        Create the :class:`Friendship` between
        :attr:`~FriendshipRequest.from_user` and
        :attr:`~FriendshipRequest.to_user` and mark this instance
        as accepted.

        :obj:`~friends.signals.friendship_accepted` is signalled on success.

        .. seealso::

            :class:`~friends.views.FriendshipAcceptView`
        """
        Friendship.objects.befriend(self.from_user, self.to_user)
        self.accepted = True
        self.save()
        signals.friendship_accepted.send(sender=self)

    def decline(self):
        """
        Deletes this :class:`FriendshipRequest`

        :obj:`~friends.signals.friendship_declined` is signalled on success.

        .. seealso::

            :class:`~friends.views.FriendshipDeclineView`
        """
        signals.friendship_declined.send(sender=self)
        self.delete()

    def cancel(self):
        """
        Deletes this :class:`FriendshipRequest`

        :obj:`~friends.signals.friendship_cancelled` is signalled on success.

        .. seealso::

            :class:`~friends.views.FriendshipCancelView`
        """
        signals.friendship_cancelled.send(sender=self)
        self.delete()


class FriendshipManager(models.Manager):
    def friends_of(self, user, shuffle=False):
        """
        List friends of ``user``.

        :param user: User to query friends.
        :type user: |User|
        :param shuffle: Optional. Default ``False``.
        :type shuffle: |bool|
        :returns: :class:`~django.db.models.query.QuerySet` containing friends
                  of ``user``.
        """
        qs = User.objects.filter(friendship__friends__user=user)
        if shuffle:
            qs = qs.order_by('?')
        return qs

    def are_friends(self, user1, user2):
        """
        Indicate if ``user1`` and ``user2`` are friends.

        :param user1: User to compare with ``user2``.
        :type user1: |User|
        :param user2: User to compare with ``user1``.
        :type user2: |User|
        :rtype: |bool|
        """
        friendship = Friendship.objects.get(user=user1)
        return bool(friendship.friends.filter(user=user2).exists())

    def befriend(self, user1, user2):
        """
        Establish friendship between ``user1`` and ``user2``.

        .. important::

            Instead of calling this method directly,
            :func:`FriendshipRequest.accept()
            <friends.models.FriendshipRequest.accept>`, which calls
            this method, should be used.

        :param user1: User to make friends with ``user2``.
        :type user1: |User|
        :param user2: User to make friends with ``user1``.
        :type user2: |User|
        """
        friendship = Friendship.objects.get(user=user1)
        friendship.friends.add(Friendship.objects.get(user=user2))
        # Now that user1 accepted user2's friend request we should delete any
        # request by user1 to user2 so that we don't have ambiguous data
        FriendshipRequest.objects.filter(from_user=user1,
                                         to_user=user2).delete()

    def unfriend(self, user1, user2):
        """
        Break friendship between ``user1`` and ``user2``.

        :param user1: User to unfriend with ``user2``.
        :type user1: |User|
        :param user2: User to unfriend with ``user1``.
        :type user2: |User|
        """
        # Break friendship link between users
        friendship = Friendship.objects.get(user=user1)
        friendship.friends.remove(Friendship.objects.get(user=user2))
        # Delete FriendshipRequest's as well
        FriendshipRequest.objects.filter(from_user=user1,
                                         to_user=user2).delete()
        FriendshipRequest.objects.filter(from_user=user2,
                                         to_user=user1).delete()


class Friendship(models.Model):
    """
    Represents the network of friendships.
    """

    user = models.OneToOneField(User, related_name='friendship')
    """
    |OneToOneField| to |User| whose friends are stored.
    """

    friends = models.ManyToManyField('self', symmetrical=True)
    """
    Symmetrical |ManyToManyField| to :class:`Friendship`.

    .. seealso::

        To obtain friends as a list of |User|'s use
        :meth:`FriendshipManager.friends_of()
        <friends.models.FriendshipManager.friends_of>`.
    """

    objects = FriendshipManager()

    class Meta:
        verbose_name = _(u'friendship')
        verbose_name_plural = _(u'friendships')

    def __unicode__(self):
        return _(u'%(user)s\'s friends') % {'user': unicode(self.user)}

    def friend_count(self):
        """
        Return the count of :attr:`~Friendship.friends`.
        This method is used in :class:`~friends.admin.FriendshipAdmin`.

        :rtype: |int|
        """
        return self.friends.count()
    friend_count.short_description = _(u'Friends count')

    def friend_summary(self, count=7):
        """
        Return a string representation of
        :attr:`~Friendship.friends`.
        This method is used in :class:`~friends.admin.FriendshipAdmin`.

        :param |int| count: Maximum number of friends to include in the output.
        :rtype: |unicode|
        """
        friend_list = self.friends.all().select_related(depth=1)[:count]
        return u'[%s%s]' % (u', '.join(unicode(f.user) for f in friend_list),
                            u', ...' if self.friend_count() > count else u'')
    friend_summary.short_description = _(u'Summary of friends')


class UserBlocks(models.Model):
    """
    |User|'s blocked by :attr:`~UserBlocks.user`.
    """

    user = models.OneToOneField(User, related_name='user_blocks')
    """
    |OneToOneField| to |User| whose blocks are stored.
    """

    blocks = models.ManyToManyField(User, related_name='blocked_by_set')
    """
    |ManyToManyField| to containing blocked |User|'s.
    """

    class Meta:
        verbose_name = verbose_name_plural = _(u'user blocks')

    def __unicode__(self):
        return _(u'Users blocked by %(user)s') % {'user': unicode(self.user)}

    def block_count(self):
        """
        Return the count of :attr:`~UserBlocks.blocks`.
        This method is used in :class:`~friends.admin.UserBlocksAdmin`.

        :rtype: |int|
        """
        return self.blocks.count()
    block_count.short_description = _(u'Blocks count')

    def block_summary(self, count=7):
        """
        Return a string representation of
        :attr:`~UserBlocks.blocks`.
        This method is used in :class:`~friends.admin.UserBlocksAdmin`.

        :param |int| count: Maximum number of blocked users to include in
                            the output.
        :rtype: |unicode|
        """
        block_list = self.blocks.all()[:count]
        return u'[%s%s]' % (u', '.join(unicode(user) for user in block_list),
                            u', ...' if self.block_count() > count else u'')
    block_summary.short_description = _(u'Summary of blocks')


# Signal connections
models.signals.post_save.connect(
    signals.create_friendship_instance,
    sender=User,
    dispatch_uid='friends.signals.create_friendship_instance',
)
models.signals.post_save.connect(
    signals.create_userblocks_instance,
    sender=User,
    dispatch_uid='friends.signals.create_userblocks_instance',
)
