from django.conf import settings


REDIRECT_FALLBACK_TO_PROFILE = getattr(settings,
                                       'FRIENDS_REDIRECT_FALLBACK_TO_PROFILE',
                                       False)
