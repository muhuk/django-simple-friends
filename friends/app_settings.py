from django.conf import settings


REDIRECT_FALLBACK_TO_PROFILE = getattr(settings,
                                       'FRIENDS_REDIRECT_FALLBACK_TO_PROFILE',
                                       False)

# During syncdb, this app ensures a Friendship and UserBlock record exists for
# each user. This setting controls the batch size on the bulk creation of those
# records when that process runs.
FRIENDS_SYNCDB_BATCH_SIZE = getattr(settings, 'FRIENDS_SYNCDB_BATCH_SIZE', 999)
