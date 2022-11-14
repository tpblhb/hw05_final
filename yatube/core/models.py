from behaviors.behaviors import Timestamped
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class DefaultModel(models.Model):
    class Meta:
        abstract = True


class TimestampedModel(DefaultModel, Timestamped):
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-created',)
        abstract = True


class TextParams(TimestampedModel):
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
