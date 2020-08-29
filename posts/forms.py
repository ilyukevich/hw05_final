from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Post
from .models import Comment
from django.forms import ModelForm


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': _('Группа'),
            'text': _('Текст'),
            'image': _('Изображение'),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': _('Комментарий'),
        }
