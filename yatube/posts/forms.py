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

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == "":
            raise forms.ValidationError(
                'Поле "Текст поста" должно быть заполнено'
            )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий'}
        help_texts = {'text': 'Прокомментируйте'}
