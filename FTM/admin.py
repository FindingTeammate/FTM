from django.contrib import admin
from .models import Profile, WorkExp, Reviews


# Register your models here.
class ProfileList(admin.ModelAdmin):
    list_display = ('user', 'techstack','certificates')
    list_filter = ('user','techstack')
    search_fields = ('user',)
    ordering = ['user']


admin.site.register(Profile)
admin.site.register(WorkExp)
admin.site.register(Reviews)
