from django.contrib import admin

from core.admin import BaseAdmin
from posts.models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    list_filter = ('pub_date',)
    search_fields = ('text',)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    list_display = (
        'pk',
        'title',
    )
    search_fields = ('title',)


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )
    search_fields = ('user',)
    list_filter = ('author',)
