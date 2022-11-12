from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TextParams(models.Model):
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True,
    )
    text = text = models.TextField(
        verbose_name='текст',
        help_text='введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )

    class Meta:
        abstract = True
