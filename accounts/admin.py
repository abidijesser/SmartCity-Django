from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'telephone', 'linked_uri')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'role')
    fields = ('user', 'role', 'telephone', 'linked_uri')
