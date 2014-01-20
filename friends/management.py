from django.db.models.signals import post_syncdb
from django.contrib.auth.models import User
import models


def post_syncdb_handler(sender, app, created_models, verbosity, **kwargs):
    friends_model_created = models.Friendship in created_models
    block_model_created = models.UserBlocks in created_models
    app_models = []
    if friends_model_created:
        app_models.append(models.Friendship)
    if block_model_created:
        app_models.append(models.UserBlocks)
    if not app_models:
        return
    user_ids = User.objects.values_list('pk', flat=True).order_by('pk')
    for model in app_models:
        name = model.__name__
        if verbosity >= 1:
            print "Creating {0} models for existing users...".format(name)
        existing_ids = model.objects.values_list('pk', flat=True)
        # Convert to set for faster lookups: O(1) vs O(n)
        existing_ids = set(existing_ids)
        # We only want user IDs that don't have existing Friendship records.
        # For example, a superuser account created interactively during syncdb
        # will have a Friendship record due to this app's post_save signal
        # handler
        user_ids = [i for i in user_ids if i not in existing_ids]
        batch = []
        for user_id in user_ids:
            batch.append(model(user_id=user_id))
        model.objects.bulk_create(batch)
        if verbosity >= 2 or True:
            print "Created {0} new {1} record(s).".format(len(user_ids), name)


post_syncdb.connect(
    post_syncdb_handler,
    sender=models,
    dispatch_uid='friends.signals.post_syncdb',
)
