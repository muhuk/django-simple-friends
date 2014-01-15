from django.db.models.signals import post_syncdb
from django.contrib.auth.models import User
import models


def post_syncdb_handler(sender, app, created_models, verbosity, **kwargs):
    if verbosity >= 1:
        print "Creating Friendship & UserBlocks models for existing users..."
    user_ids = User.objects.values_list('pk', flat=True).order_by('pk')
    friendship_total = userblocks_total = 0
    for user_id in user_ids:
        obj, created = models.Friendship.objects.get_or_create(user_id=user_id)
        if created:
            friendship_total += 1
        obj, created = models.UserBlocks.objects.get_or_create(user_id=user_id)
        if created:
            userblocks_total += 1
    if verbosity >= 2 or True:
        print "Created {0} new Friendships & {1} new UserBlocks.".format(
            friendship_total, userblocks_total)


post_syncdb.connect(
    post_syncdb_handler,
    sender=models,
    dispatch_uid='friends.signals.post_syncdb',
)
