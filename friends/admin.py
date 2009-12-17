from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from models import FriendshipRequest, Friendship, UserBlocks


class FriendshipRequestAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('from_user', 'to_user', 'accepted', 'created')
    list_filter = ('accepted',)
    actions = ('accept_friendship', 'decline_friendship', 'cancel_friendship')

    def accept_friendship(self, request, queryset):
        for friendship_request in queryset:
            friendship_request.accept()
    accept_friendship.short_description = _(u'Accept selected friendship ' \
                                            u'requests')


    def decline_friendship(self, request, queryset):
        for friendship_request in queryset:
            friendship_request.decline()
    decline_friendship.short_description = _(u'Decline selected friendship ' \
                                             u'requests')


    def cancel_friendship(self, request, queryset):
        for friendship_request in queryset:
            friendship_request.cancel()
    cancel_friendship.short_description = _(u'Cancel selected friendship ' \
                                            u'requests')
admin.site.register(FriendshipRequest, FriendshipRequestAdmin)


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend_count', 'friend_summary')
admin.site.register(Friendship, FriendshipAdmin)


class UserBlocksAdmin(admin.ModelAdmin):
    list_display = ('user', 'block_count', 'block_summary')
admin.site.register(UserBlocks, UserBlocksAdmin)
