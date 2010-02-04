import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import signals


class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="invitations_from")
    to_user = models.ForeignKey(User, related_name="invitations_to")
    message = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(default=datetime.datetime.now,
                                   editable=False)
    accepted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _(u'friendship request')
        verbose_name_plural = _(u'friendship requests')
        unique_together = (('to_user', 'from_user'),)

    def __unicode__(self):
        return _(u'%(from_user)s wants to be friends with %(to_user)s') % \
                    {'from_user': unicode(self.from_user),
                     'to_user': unicode(self.to_user)}

    def accept(self):
        Friendship.objects.befriend(self.from_user, self.to_user)
        self.accepted = True
        self.save()
        signals.friendship_accepted.send(sender=self)

    def decline(self):
        signals.friendship_declined.send(sender=self, cancelled=False)
        self.delete()

    def cancel(self):
        signals.friendship_declined.send(sender=self, cancelled=True)
        self.delete()


class FriendshipManager(models.Manager):
    def friends_of(self, user, shuffle=False):
        qs = User.objects.filter(friendship__friends__user=user)
        if shuffle:
            qs = qs.order_by('?')
        return qs

    def are_friends(self, user1, user2):
        return bool(Friendship.objects.get(user=user1).friends.filter(
                                                          user=user2).count())

    def befriend(self, user1, user2):
        Friendship.objects.get(user=user1).friends.add(
                                           Friendship.objects.get(user=user2))

    def unfriend(self, user1, user2):
        Friendship.objects.get(user=user1).friends.remove(
                                           Friendship.objects.get(user=user2))


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


def create_friendship_instance(sender, instance, created, raw, **kwargs):
    if created and not raw:
        Friendship.objects.create(user=instance)
models.signals.post_save.connect(create_friendship_instance,
                                 sender=User,
                                 dispatch_uid='friends.models.create_' \
                                              'friendship_instance')


def create_userblocks_instance(sender, instance, created, raw, **kwargs):
    if created and not raw:
        UserBlocks.objects.create(user=instance)
models.signals.post_save.connect(create_userblocks_instance,
                                 sender=User,
                                 dispatch_uid='friends.models.create_' \
                                              'userblocks_instance')
