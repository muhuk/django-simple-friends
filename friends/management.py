from django.db.models.signals import post_syncdb
import models
#from django.contrib.auth.models import User
import signals


post_syncdb.connect(
    signals.create_friendship_instance_post_syncdb,
    sender=models,
    dispatch_uid='friends.signals.create_friendship_instance_post_syncdb',
)
post_syncdb.connect(
    signals.create_userblock_instance_post_syncdb,
    sender=models,
    dispatch_uid='friends.signals.create_userblock_instance_post_syncdb',
)
