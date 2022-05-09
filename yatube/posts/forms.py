from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text",)
        labels = {
            "group": "Группа",
            "text": "Текст"
        }
        help_texts = {'text': 'Напишите текст поста',
                      'group': 'Группа поста'}
