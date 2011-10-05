from django.dispatch import Signal


friendship_accepted = Signal()


friendship_declined = Signal(providing_args=['cancelled'])


def create_friendship_instance(sender, instance, created, raw, **kwargs):
    from friends.models import Friendship
    if created and not raw:
        Friendship.objects.create(user=instance)


def create_userblocks_instance(sender, instance, created, raw, **kwargs):
    from friends.models import UserBlocks
    if created and not raw:
        UserBlocks.objects.create(user=instance)
