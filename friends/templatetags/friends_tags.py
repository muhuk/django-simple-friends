from django import template
from django.contrib.auth.models import User
from friends.models import FriendshipRequest, Friendship, UserBlocks


register = template.Library()


@register.tag
def friends_of(parser, token):
    tag_name, user_var = token.split_contents()
    return FriendsOfNode(user_var)


class FriendsOfNode(template.Node):
    def __init__(self, user_var):
        self.user_var = template.Variable(user_var)

    def render(self, context):
        user = self.user_var.resolve(context)
        context.update({'friends': Friendship.objects.friends_of(user, True)})
        return u''


@register.tag
def add_to_friends(parser, token):
    bits = token.split_contents()
    tag_name, bits = bits[0], bits[1:]
    if not bits:
        raise template.TemplateSyntaxError(
                           '%s tag requires at least one argument' % tag_name)
    elif len(bits) > 3:
        raise template.TemplateSyntaxError(
                            '%s tag takes at most three arguments' % tag_name)
    if len(bits) == 3:
        if bits[2].startswith('"') and bits[2].endswith('"'):
            bits[2] = bits[2][1:-1]
        else:
            raise template.TemplateSyntaxError(
                      'Third argument for %s tag must be a string' % tag_name)
    return AddToFriendsNode(*bits)


class AddToFriendsNode(template.Node):
    def __init__(self, target_user, current_user='user',
                       template_name='friends/includes/add_to_friends.html'):
        self.target_user = template.Variable(target_user)
        self.current_user = template.Variable(current_user)
        self.template_name = template_name

    def render(self, context):
        target_user = self.target_user.resolve(context)
        current_user = self.current_user.resolve(context)
        if current_user.is_authenticated():
            ctx = {'target_user': target_user,
                   'current_user': current_user}
            if not target_user is current_user:
                ctx['are_friends'] = Friendship.objects.are_friends(
                                                    target_user, current_user)
                ctx['is_invited'] = bool(FriendshipRequest.objects.filter(
                                                    from_user=current_user,
                                                    to_user=target_user,
                                                    accepted=False).count())
            return template.loader.render_to_string(self.template_name,
                                                    ctx,
                                                    context)
        else:
            return u''


@register.tag
def block_user(parser, token):
    bits = token.split_contents()
    tag_name, bits = bits[0], bits[1:]
    if not bits:
        raise template.TemplateSyntaxError(
                           '%s tag requires at least one argument' % tag_name)
    elif len(bits) > 3:
        raise template.TemplateSyntaxError(
                            '%s tag takes at most three arguments' % tag_name)
    if len(bits) == 3:
        if bits[2].startswith('"') and bits[2].endswith('"'):
            bits[2] = bits[2][1:-1]
        else:
            raise template.TemplateSyntaxError(
                      'Third argument for %s tag must be a string' % tag_name)
    return BlockUserLinkNode(*bits)


class BlockUserLinkNode(template.Node):
    def __init__(self, target_user, current_user='user',
                       template_name='friends/includes/block_user.html'):
        self.target_user = template.Variable(target_user)
        self.current_user = template.Variable(current_user)
        self.template_name = template_name

    def render(self, context):
        target_user = self.target_user.resolve(context)
        current_user = self.current_user.resolve(context)
        if current_user.is_authenticated():
            ctx = {'target_user': target_user,
                   'current_user': current_user}
            if not target_user is current_user:
                ctx['is_blocked'] = bool(UserBlocks.objects.filter(
                         user=current_user, blocks__pk=target_user.pk).count())
            return template.loader.render_to_string(self.template_name,
                                                    ctx,
                                                    context)
        else:
            return u''


def _get_user(value):
    if isinstance(value, User):
        return value
    elif hasattr(value, 'user') and isinstance(value.user, User):
        return value.user
    else:
        raise ValueError


@register.filter
def blocked_by(value, arg):
    try:
        user = _get_user(value)
    except ValueError:
        raise template.TemplateSyntaxError('blocked_by filter can only be ' \
                                           'applied to User\'s or objects ' \
                                           'with a `user` attribute.')
    try:
        target = _get_user(arg)
    except ValueError:
        raise template.TemplateSyntaxError('blocked_by filter\'s argument ' \
                                           'must be a User or an object ' \
                                           'with a `user` attribute.')
    if UserBlocks.objects.filter(user=target, blocks=user).count():
        return True
    else:
        return False
