from django.contrib.auth import get_user_model
from django.db import models

from core.models import author, pub_date, text
from core.utils import truncatechars

User = get_user_model()

MAX_TEXT_LENGTH = 15
MAX_TITLE_LENGTH = 20


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
        return truncatechars(self.title, MAX_TITLE_LENGTH)


class Post(models.Model):
    text = text()
    pub_date = pub_date()
    author = author()
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

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return truncatechars(self.text, MAX_TEXT_LENGTH)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        help_text='комментарий к посту',
    )
    author = author()
    text = text()
    created = pub_date()

    def __str__(self) -> str:
        return f'{self.text[:MAX_TEXT_LENGTH]}, author:{self.author}'

    class Meta:
        ordering = ('-created',)


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
