from django.db.models.signals import post_syncdb
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
import models
from app_settings import FRIENDS_SYNCDB_BATCH_SIZE


def post_syncdb_handler(sender, app, created_models, verbosity, **kwargs):
    if FRIENDS_SYNCDB_BATCH_SIZE < 1:
        raise ImproperlyConfigured("FRIENDS_SYNCDB_BATCH_SIZE must be > 0")
    for model in (models.Friendship, models.UserBlocks):
        name = model.__name__
        if verbosity >= 1:
            print "Creating {0} models for existing users...".format(name)
        # We only want user IDs that don't have existing Friendship or
        # UserBlock records. For example, a superuser account created
        # interactively during syncdb will have such a record due to this
        # app's post_save signal handler
        if model == models.Friendship:
            kwargs = { 'friendship__isnull': True }
        else:
            kwargs = { 'user_blocks__isnull': True }
        user_ids = User.objects.filter(**kwargs).values_list('pk', flat=True)\
            .order_by('pk')
        # Note: In Django 1.5, a batch_size parameter can be passed directly to
        # bulk_create(). Better to use that parameter instead of the below
        # code once version 1.4 is no longer supported by this app.
        batch = []
        count = 0
        for user_id in user_ids:
            batch.append(model(user_id=user_id))
            count += 1
            if count == FRIENDS_SYNCDB_BATCH_SIZE:
                model.objects.bulk_create(batch)
                batch = []
                count = 0
        if batch:
            model.objects.bulk_create(batch)
        if verbosity >= 2 or True:
            print "Created {0} new {1} record(s).".format(len(user_ids), name)


post_syncdb.connect(
    post_syncdb_handler,
    sender=models,
    dispatch_uid='friends.signals.post_syncdb',
)
