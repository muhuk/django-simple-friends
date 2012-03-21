from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'friends.views',
    url(r'^add/(?P<username>[\+\w\.@-_]+)/$',
        'friendship_request',
        name='friendship_request'),
    url(r'^accept/(?P<username>[\+\w\.@-_]+)/$',
        'friendship_accept',
        name='friendship_accept'),
    url(r'^decline/(?P<username>[\+\w\.@-_]+)/$',
        'friendship_decline',
        name='friendship_decline'),
    url(r'^cancel/(?P<username>[\+\w\.@-_]+)/$',
        'friendship_cancel',
        name='friendship_cancel'),
    url(r'^delete/(?P<username>[\+\w\.@-_]+)/$',
        'friendship_delete',
        name='friendship_delete'),
    url(r'^block/(?P<username>[\+\w\.@-_]+)/$',
        'user_block',
        name='user_block'),
    url(r'^unblock/(?P<username>[\+\w\.@-_]+)/$',
        'user_unblock',
        name='user_unblock'),
)
