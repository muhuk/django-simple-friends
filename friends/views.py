"""
Views
=====

.. _class-based-views:

Class Based Views
-----------------

All the views are implemented as
`classes <https://docs.djangoproject.com/en/dev/topics/class-based-views/>`_
but :ref:`view functions <view-functions>` are also provided.

.. autoclass:: BaseActionView
    :members:

.. autoclass:: FriendshipAcceptView

.. autoclass:: UserBlockView

.. autoclass:: FriendshipCancelView

.. autoclass:: FriendshipDeclineView

.. autoclass:: FriendshipDeleteView

.. autoclass:: FriendshipRequestView

.. autoclass:: FriendshipUnblockView


.. _view-functions:

View Functions
--------------

.. tip:: If you want to customize the views provided, check out :ref:`class-based-views` first.

.. autofunction:: friendship_request

.. autofunction:: friendship_accept

.. autofunction:: friendship_decline

.. autofunction:: friendship_cancel

.. autofunction:: friendship_delete

.. autofunction:: user_block

.. autofunction:: user_unblock
"""

from django.http import HttpResponseBadRequest, Http404
from django.db import transaction
from django.views.generic.base import RedirectView
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from models import FriendshipRequest, Friendship
from app_settings import REDIRECT_FALLBACK_TO_PROFILE


class BaseActionView(RedirectView):
    """
    Base class for action views.
    """

    http_method_names = ['get', 'post']
    permanent = False

    def action(request, user, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement action()")

    def get(self, request, username, *args, **kwargs):
        if request.user.username == username:
            return HttpResponseBadRequest(ugettext(u'You can\'t befriend ' \
                                                   u'yourself.'))
        user = get_object_or_404(User, username=username)
        self.action(request, user, *args, **kwargs)
        self.set_url(request, **kwargs)
        return super(BaseActionView, self).get(request, **kwargs)

    def set_url(self, request, **kwargs):
        """
        Set the ``url`` attribute so that it can be used when
        :py:meth:`~django.views.generic.base.RedirectView.get_redirect_url` is
        called.

        ``url`` is determined using the following methods, in order:

        - It can be set in the urlconf using ``redirect_to`` keyword argument.
        - If ``redirect_to_param`` keyword argument is set in urlconf, the
          request parameter with that name will be used. In this case the
          request parameter **must** be provided in runtime.
        - If the request has ``redirect_to`` to parameter is present, its
          value will be used.
        - If ``REDIRECT_FALLBACK_TO_PROFILE`` setting is ``True``, current
          user's profile URL will be used.
        - ``HTTP_REFERER`` header's value will be used if exists.
        - If all else fail, ``'/'`` will be used.
        """
        if 'redirect_to' in kwargs:
            self.url = kwargs['redirect_to']
        elif 'redirect_to_param' in kwargs and \
                                kwargs['redirect_to_param'] in request.REQUEST:
            self.url = request.REQUEST[kwargs['redirect_to_param']]
        elif 'redirect_to' in request.REQUEST:
            self.url = request.REQUEST['next']
        elif REDIRECT_FALLBACK_TO_PROFILE:
            self.url = request.user.get_profile().get_absolute_url()
        else:
            self.url = request.META.get('HTTP_REFERER', '/')


class FriendshipAcceptView(BaseActionView):
    @transaction.commit_on_success
    def accept_friendship(self, from_user, to_user):
        get_object_or_404(FriendshipRequest,
                          from_user=from_user,
                          to_user=to_user).accept()

    def action(self, request, user, **kwargs):
        self.accept_friendship(user, request.user)


class FriendshipRequestView(FriendshipAcceptView):
    @transaction.commit_on_success
    def action(self, request, user, **kwargs):
        if Friendship.objects.are_friends(request.user, user):
            raise RuntimeError('%r amd %r are already friends' % \
                                                          (request.user, user))
        try:
            # If there's a friendship request from the other user accept it.
            self.accept_friendship(user, request.user)
        except Http404:
            request_message = request.REQUEST.get('message', u'')
            # If we already have an active friendship request IntegrityError
            # will be raised and the transaction will be rolled back.
            FriendshipRequest.objects.create(from_user=request.user,
                                             to_user=user,
                                             message=request_message)


class FriendshipDeclineView(BaseActionView):
    def action(self, request, user, **kwargs):
        get_object_or_404(FriendshipRequest,
                          from_user=user,
                          to_user=request.user).decline()


class FriendshipCancelView(BaseActionView):
    def action(self, request, user, **kwargs):
        get_object_or_404(FriendshipRequest,
                          from_user=request.user,
                          to_user=user).cancel()


class FriendshipDeleteView(BaseActionView):
    def action(self, request, user, **kwargs):
        Friendship.objects.unfriend(request.user, user)


class UserBlockView(BaseActionView):
    def action(self, request, user, **kwargs):
        request.user.user_blocks.blocks.add(user)


class FriendshipUnblockView(BaseActionView):
    def action(self, request, user, **kwargs):
        request.user.user_blocks.blocks.remove(user)


friendship_request = login_required(FriendshipRequestView.as_view())
friendship_accept = login_required(FriendshipAcceptView.as_view())
friendship_decline = login_required(FriendshipDeclineView.as_view())
friendship_cancel = login_required(FriendshipCancelView.as_view())
friendship_delete = login_required(FriendshipDeleteView.as_view())
user_block = login_required(UserBlockView.as_view())
user_unblock = login_required(FriendshipUnblockView.as_view())
