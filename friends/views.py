from django.core.paginator import Paginator, InvalidPage
from django.http import HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.db import IntegrityError, transaction
from django.conf import settings
from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from models import FriendshipRequest, Friendship


def limit_to_others(f):
    def _f(request, username, *args, **kwargs):
        if request.user.username == username:
            return HttpResponseBadRequest(ugettext(u'You can\'t befriend ' \
                                                   u'yourself.'))
        return f(request, username, *args, **kwargs)
    return _f


def apply_redirect_to(f):
    def _f(request, *args, **kwargs):
        if 'redirect_to' in kwargs:
            return f(request, *args, **kwargs)
        elif 'redirect_to_param' in kwargs and \
             kwargs['redirect_to_param'] in request.REQUEST:
            redirect_to = request.REQUEST[kwargs['redirect_to_param']]
        elif 'redirect_to' in request.REQUEST:
            redirect_to = request.REQUEST['next']
        else:
            if getattr(settings,'FRIENDS_REDIRECT_FALLBACK_TO_PROFILE',False):
                redirect_to = request.user.get_profile().get_absolute_url()
            else:
                redirect_to = request.META.get('HTTP_REFERER', '/')
        return f(request, redirect_to=redirect_to, *args, **kwargs)
    return _f


def apply_other_user(f):
    def _f(request, username, redirect_to, *args, **kwargs):
        other_user = get_object_or_404(User, username=username)
        if Friendship.objects.are_friends(request.user, other_user):
            message = ugettext(u'You are already friends with %(user)s')
            request.user.message_set.create(message=message % {
                   'user': other_user.get_full_name() or other_user.username})
            return HttpResponseRedirect(redirect_to)
        else:
            return f(request, username, redirect_to, other_user, *args,
                                                                     **kwargs)
    return _f


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
                                            'outgoing': outgoing_requests }
    extra_context['user_blocks'] = request.user.user_blocks.blocks.all()
    return object_list(request,
                       queryset=friends,
                       paginate_by=paginate_by,
                       page=page,
                       allow_empty=allow_empty,
                       template_name=template_name,
                       extra_context=extra_context,
                       template_object_name=template_object_name)


@login_required
@limit_to_others
@apply_redirect_to
@apply_other_user
@transaction.commit_manually
def friendship_request(request, username, redirect_to, other_user, **kwargs):
    try:
        reverse_invitation = FriendshipRequest.objects.get(
                                   from_user=other_user, to_user=request.user)
    except FriendshipRequest.DoesNotExist:
        pass
    else:
        result = _friendship_accept(other_user, request.user, redirect_to)
        transaction.commit()
        return result
    request_message = request.REQUEST.get('message', u'')
    try:
        friendship = FriendshipRequest.objects.create(from_user=request.user,
                                                      to_user=other_user,
                                                      message=request_message)
    except IntegrityError:
        transaction.rollback()
        message = ugettext(u'You already have an active friend ' \
                                                  u'invitation for %(user)s.')
    else:
        message = ugettext(u'You have requested to be friends with %(user)s.')
    request.user.message_set.create(message=message % {
                   'user': other_user.get_full_name() or other_user.username})
    transaction.commit()
    return HttpResponseRedirect(redirect_to)


@login_required
@limit_to_others
@apply_redirect_to
@apply_other_user
def friendship_accept(request, username, redirect_to, other_user, **kwargs):
    return _friendship_accept(other_user, request.user, redirect_to)


def _friendship_accept(from_user, to_user, redirect_to):
    friendship_request_ = get_object_or_404(FriendshipRequest,
                                            from_user=from_user,
                                            to_user=to_user)
    friendship = friendship_request_.accept()
    message = ugettext(u'You are now friends with %(user)s.')
    to_user.message_set.create(message=message % {
                     'user': from_user.get_full_name() or from_user.username})
    from_user.message_set.create(message=message % {
                         'user': to_user.get_full_name() or to_user.username})
    return HttpResponseRedirect(redirect_to)


@login_required
@limit_to_others
@apply_redirect_to
@apply_other_user
def friendship_decline(request, username, redirect_to, other_user, **kwargs):
    friendship_request_ = get_object_or_404(FriendshipRequest,
                                            from_user=other_user,
                                            to_user=request.user)
    friendship = friendship_request_.decline()
    message = ugettext(u'You declined friendship request of %(user)s.')
    request.user.message_set.create(message=message % {
                   'user': other_user.get_full_name() or other_user.username})
    message = ugettext(u'%(user)s has declined your friendship request.')
    other_user.message_set.create(message=message % {
               'user': request.user.get_full_name() or request.user.username})
    return HttpResponseRedirect(redirect_to)


@login_required
@limit_to_others
@apply_redirect_to
@apply_other_user
def friendship_cancel(request, username, redirect_to, other_user, **kwargs):
    friendship_request_ = get_object_or_404(FriendshipRequest,
                                            from_user=request.user,
                                            to_user=other_user)
    friendship = friendship_request_.cancel()
    message = ugettext(u'You cancelled your request to be friends ' \
                       u'with %(user)s.')
    request.user.message_set.create(message=message % {
                   'user': other_user.get_full_name() or other_user.username})
    return HttpResponseRedirect(redirect_to)


@login_required
@limit_to_others
@apply_redirect_to
def friendship_delete(request, username, redirect_to, **kwargs):
    other_user = get_object_or_404(User, username=username)
    if Friendship.objects.are_friends(request.user, other_user) is False:
        raise Http404('You are not friends with %s.' % \
                         (other_user.get_full_name() or other_user.username,))
    Friendship.objects.unfriend(request.user, other_user)
    message = ugettext(u'You are no longer friends with %(user)s.')
    request.user.message_set.create(message=message % {
                   'user': other_user.get_full_name() or other_user.username})
    message = ugettext(u'%(user)s has removed you as a friend.')
    other_user.message_set.create(message=message % {
               'user': request.user.get_full_name() or request.user.username})
    return HttpResponseRedirect(redirect_to)


@login_required
@limit_to_others
@apply_redirect_to
def block_user(request, username, redirect_to, **kwargs):
    other_user = get_object_or_404(User, username=username)
    try:
        request.user.user_blocks.blocks.get(pk=other_user.pk)
    except User.DoesNotExist:
        request.user.user_blocks.blocks.add(other_user)
        message = ugettext(u'You have blocked %(user)s.')
    else:
        message = ugettext(u'%(user)s is already blocked.')
    request.user.message_set.create(message=message % {
                   'user': other_user.get_full_name() or other_user.username})
    return HttpResponseRedirect(redirect_to)


@login_required
@limit_to_others
@apply_redirect_to
def unblock_user(request, username, redirect_to, **kwargs):
    other_user = get_object_or_404(User, username=username)
    try:
        request.user.user_blocks.blocks.get(pk=other_user.pk)
    except User.DoesNotExist:
        message = ugettext(u'%(user)s was not blocked.')
    else:
        request.user.user_blocks.blocks.remove(other_user)
        message = ugettext(u'You have unblocked %(user)s.')
    request.user.message_set.create(message=message % {
                   'user': other_user.get_full_name() or other_user.username})
    return HttpResponseRedirect(redirect_to)
