from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image',
        )
        help_text = {
            'username': 'Имя на платформе, должно быть уникально.',
            'password': 'Должен включать: заглавные/строчные буквы, цифры.',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {'text': 'Прокомментируйте'}
