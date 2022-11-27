from django.contrib import admin
from .models import Profile, WorkExp, Reviews
# from .models import FriendList, FriendRequest


# Register your models here.
class ProfileList(admin.ModelAdmin):
    list_display = ('user', 'techstack','certificates')
    list_filter = ('user','techstack')
    search_fields = ('user',)
    ordering = ['user']


admin.site.register(Profile)
admin.site.register(WorkExp)
admin.site.register(Reviews)


# class FriendListAdmin(admin.ModelAdmin):
#     list_filter = ['user']
#     list_display = ['user']
#     search_fields = ['user']
#     readonly_fields = ['user']
#
#     class Meta:
#         model = FriendList


# admin.site.register(FriendList)


# class FriendRequestAdmin(admin.ModelAdmin):
#     list_filter = ['sender', 'receiver']
#     list_display = ['sender', 'receiver']
#     search_fields = ['sender_username', 'receiver_username']
#     readonly_fields = ['user']

    # class Meta:
    #     model = FriendRequest

#
# admin.site.register(FriendRequest)

