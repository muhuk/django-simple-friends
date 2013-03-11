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
        a :class:`FriendshipRequest` from `to_user` to `from_user`.
    """

    from_user = models.ForeignKey(User, related_name="friendshiprequests_from")
    """
    :class:`~django.db.models.ForeignKey` to
    :class:`~django.contrib.auth.models.User` who initiated the request.
    """

    to_user = models.ForeignKey(User, related_name="friendshiprequests_to")
    """
    :class:`~django.db.models.ForeignKey` to
    :class:`~django.contrib.auth.models.User` the request has been sent.
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
        return _(u'%(from_user)s wants to be friends with %(to_user)s') % \
                    {'from_user': unicode(self.from_user),
                     'to_user': unicode(self.to_user)}

    def accept(self):
        """
        Create the :class:`~friends.models.Friendship` between
        :attr:`~friends.models.FriendshipRequest.from_user` and
        :attr:`~friends.models.FriendshipRequest.to_user` and mark this instance
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
        Deletes this :class:`~friends.models.FriendshipRequest`

        :obj:`~friends.signals.friendship_declined` is signalled on success.

        .. seealso::
            :class:`~friends.views.FriendshipDeclineView`
        """
        signals.friendship_declined.send(sender=self)
        self.delete()

    def cancel(self):
        """
        Deletes this :class:`~friends.models.FriendshipRequest`

        :obj:`~friends.signals.friendship_cancelled` is signalled on success.

        .. seealso::
            :class:`~friends.views.FriendshipCancelView`
        """
        signals.friendship_cancelled.send(sender=self)
        self.delete()


class FriendshipManager(models.Manager):
    def friends_of(self, user, shuffle=False):
        qs = User.objects.filter(friendship__friends__user=user)
        if shuffle:
            qs = qs.order_by('?')
        return qs

    def are_friends(self, user1, user2):
        return bool(Friendship.objects.get(user=user1).friends.filter(
                                                          user=user2).exists())

    def befriend(self, user1, user2):
        Friendship.objects.get(user=user1).friends.add(
                                           Friendship.objects.get(user=user2))
        # Now that user1 accepted user2's friend request we should delete any
        # request by user1 to user2 so that we don't have ambiguous data
        FriendshipRequest.objects.filter(from_user=user1,
                                         to_user=user2).delete()

    def unfriend(self, user1, user2):
        # Break friendship link between users
        Friendship.objects.get(user=user1).friends.remove(
                                           Friendship.objects.get(user=user2))
        # Delete FriendshipRequest's as well
        FriendshipRequest.objects.filter(from_user=user1,
                                         to_user=user2).delete()
        FriendshipRequest.objects.filter(from_user=user2,
                                         to_user=user1).delete()


class Friendship(models.Model):
    user = models.OneToOneField(User, related_name='friendship')
    friends = models.ManyToManyField('self', symmetrical=True)

    objects = FriendshipManager()

    class Meta:
        verbose_name = _(u'friendship')
        verbose_name_plural = _(u'friendships')

    def __unicode__(self):
        return _(u'%(user)s\'s friends') % {'user': unicode(self.user)}

    def friend_count(self):
        return self.friends.count()
    friend_count.short_description = _(u'Friends count')

    def friend_summary(self, count=7):
        friend_list = self.friends.all().select_related(depth=1)[:count]
        return u'[%s%s]' % (u', '.join(unicode(f.user) for f in friend_list),
                            u', ...' if self.friend_count() > count else u'')
    friend_summary.short_description = _(u'Summary of friends')


class UserBlocks(models.Model):
    user = models.OneToOneField(User, related_name='user_blocks')
    blocks = models.ManyToManyField(User, related_name='blocked_by_set')

    class Meta:
        verbose_name = verbose_name_plural = _(u'user blocks')

    def __unicode__(self):
        return _(u'Users blocked by %(user)s') % {'user': unicode(self.user)}

    def block_count(self):
        return self.blocks.count()
    block_count.short_description = _(u'Blocks count')

    def block_summary(self, count=7):
        block_list = self.blocks.all()[:count]
        return u'[%s%s]' % (u', '.join(unicode(user) for user in block_list),
                            u', ...' if self.block_count() > count else u'')
    block_summary.short_description = _(u'Summary of blocks')


# Signal connections
models.signals.post_save.connect(signals.create_friendship_instance,
                                 sender=User,
                                 dispatch_uid='friends.signals.create_' \
                                              'friendship_instance')
models.signals.post_save.connect(signals.create_userblocks_instance,
                                 sender=User,
                                 dispatch_uid='friends.signals.create_' \
                                              'userblocks_instance')
