from django.contrib import admin
from .models import User, Review, Title, Genre, Comment, Category


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'title', 'text', 'score', 'pub_date')
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'review', 'text', 'pub_date')
    empty_value_display = '-пусто-'


admin.site.register(User)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Title)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Comment, CommentAdmin)
