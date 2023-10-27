from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'role',)
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'subscriber',
    )
    search_fields = ('author', 'subscriber',)
    list_filter = ('author', 'subscriber',)
    empty_value_display = '-пусто-'
