from django.contrib import admin
from .models import Post, Group

#добавил
from .models import Comment


# Register your models here.

class PostAdmin(admin.ModelAdmin):
    """fields that should be displayed in the admin panel"""
    # add column 'pk' to the beginning
    list_display = ("pk", "text", "pub_date", "author")
    # adding an interface for searching by post text
    search_fields = ("text",)
    # adding the ability to filter by date
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    """Group fields that are displayed in the admin panel"""
    list_display = ("title", "slug", "description")
    search_fields = ()
    list_filter = ()
    empty_value_display = "-пусто-"

#добавил
class CommentAdmin(admin.ModelAdmin):
    """Group fields that are displayed in the admin panel"""
    list_display = ("post", "author", "text", "created")
    search_fields = ()
    list_filter = ()
    empty_value_display = "-пусто-"

# when registering a Post model as a configuration source, assign the PostAdmin class to it
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)

#добавил
admin.site.register(Comment, CommentAdmin)
