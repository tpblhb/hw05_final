from django.contrib.auth import get_user_model
from django.db import models

from core.models import TextAuthor, TimestampedModel
from core.utils import truncatechars

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'заголовок',
        max_length=200,
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='текстовый идентификатор страницы',
    )
    description = models.TextField(
        verbose_name='описание',
    )

    def __str__(self) -> str:
        return truncatechars(self.title)


class Post(TextAuthor):
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='группа',
        help_text='выберите группу',
    )
    image = models.ImageField(
        'картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta(TimestampedModel.Meta):
        default_related_name = 'posts'
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return truncatechars(self.text)


class Comment(TextAuthor):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        help_text='комментарий к посту',
    )

    def __str__(self) -> str:
        return f'{self.text}, автор: {self.author}'

    class Meta(TimestampedModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'комментарий'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='subscribe',
            ),
        ]
