from django.db.models.signals import post_syncdb
from django.contrib.auth.models import User
import models


def post_syncdb_handler(sender, app, created_models, verbosity, **kwargs):
    if verbosity >= 1:
        print "Creating Friendship & UserBlocks models for existing users..."
    user_ids = User.objects.values_list('pk', flat=True).order_by('pk')
    total = user_ids.count()
    batch_size = 2
    for start in range(0, total, batch_size):
        friendships = []
        user_blocks = []
        for user_id in user_ids[start:min(start + batch_size, total)]:
            friendships.append(models.Friendship(user_id=user_id))
            user_blocks.append(models.UserBlocks(user_id=user_id))
        models.Friendship.objects.bulk_create(friendships)
        models.UserBlocks.objects.bulk_create(user_blocks)
    if verbosity >= 2 and total:
        print "Created Friendship & UserBlocks for {0} users.".format(total)


post_syncdb.connect(
    post_syncdb_handler,
    sender=models,
    dispatch_uid='friends.signals.post_syncdb',
)
