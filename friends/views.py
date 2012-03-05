"""
.. autofunction:: friend_list

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
from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from models import FriendshipRequest, Friendship, UserBlocks
from app_settings import REDIRECT_FALLBACK_TO_PROFILE


@login_required
def friend_list(request,
                username=None,
                paginate_by=None,
                page=None,
                allow_empty=True,
                template_name='friends/friends_list.html',
                extra_context=None,
                template_object_name='friends'):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    friends = Friendship.objects.friends_of(user)
    if extra_context is None:
        extra_context = {}
    incoming_requests = FriendshipRequest.objects.filter(
                                         to_user=request.user, accepted=False)
    outgoing_requests = FriendshipRequest.objects.filter(
                                       from_user=request.user, accepted=False)
    extra_context['target_user'] = user
    extra_context['friendship_requests'] = {'incoming': incoming_requests,
                                            'outgoing': outgoing_requests}
    try:
        user_blocks = request.user.user_blocks
    except UserBlocks.DoesNotExist:
        extra_context['user_blocks'] = []
    else:
        extra_context['user_blocks'] = user_blocks.blocks.all()

    return object_list(request,
                       queryset=friends,
                       paginate_by=paginate_by,
                       page=page,
                       allow_empty=allow_empty,
                       template_name=template_name,
                       extra_context=extra_context,
                       template_object_name=template_object_name)


class BaseFriendshipActionView(RedirectView):
    http_method_names = ['get', 'post']
    permanent = False

    def set_url(self, request, **kwargs):
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

    def get(self, request, username, *args, **kwargs):
        if request.user.username == username:
            return HttpResponseBadRequest(ugettext(u'You can\'t befriend ' \
                                                   u'yourself.'))
        user = get_object_or_404(User, username=username)
        self.action(request, user, *args, **kwargs)
        self.set_url(request, **kwargs)
        return super(BaseFriendshipActionView, self).get(request, **kwargs)


class FriendshipAcceptView(BaseFriendshipActionView):
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


class FriendshipDeclineView(BaseFriendshipActionView):
    def action(self, request, user, **kwargs):
        get_object_or_404(FriendshipRequest,
                          from_user=user,
                          to_user=request.user).decline()


class FriendshipCancelView(BaseFriendshipActionView):
    def action(self, request, user, **kwargs):
        get_object_or_404(FriendshipRequest,
                          from_user=request.user,
                          to_user=user).cancel()


class FriendshipDeleteView(BaseFriendshipActionView):
    def action(self, request, user, **kwargs):
        Friendship.objects.unfriend(request.user, user)


class FriendshipBlockView(BaseFriendshipActionView):
    def action(self, request, user, **kwargs):
        request.user.user_blocks.blocks.add(user)


class FriendshipUnblockView(BaseFriendshipActionView):
    def action(self, request, user, **kwargs):
        request.user.user_blocks.blocks.remove(user)


friendship_request = login_required(FriendshipRequestView.as_view())
friendship_accept = login_required(FriendshipAcceptView.as_view())
friendship_decline = login_required(FriendshipDeclineView.as_view())
friendship_cancel = login_required(FriendshipCancelView.as_view())
friendship_delete = login_required(FriendshipDeleteView.as_view())
user_block = login_required(FriendshipBlockView.as_view())
user_unblock = login_required(FriendshipUnblockView.as_view())
