from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


def text():
    text = models.TextField(
        verbose_name='текст',
        help_text='введите текст поста',
    )
    return text


def pub_date():
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )
    return pub_date


def author():
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    return author
