from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

MAX_TEXT_LENGTH = 15
MAX_TITLE_LENGTH = 10


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
        return (
            self.title[:MAX_TITLE_LENGTH] + '...'
            if len(self.title) > MAX_TITLE_LENGTH
            else self.title
        )


class Post(models.Model):
    text = models.TextField(
        verbose_name='текст',
        help_text='введите текст поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='группа',
        help_text='выберите группу',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return (
            self.text[:MAX_TEXT_LENGTH] + '...'
            if len(self.text) > MAX_TEXT_LENGTH
            else self.text
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        verbose_name='комментарий',
        help_text='комментарий к посту',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор комментария',
    )
    text = models.TextField(
        'текст комментария',
        help_text='введите текст комментария',
    )
    created = models.DateTimeField(
        'дата комментария',
        auto_now_add=True,
    )

    def __str__(self):
        return f'{self.text[:MAX_TEXT_LENGTH]}, author:{self.author}'

    class Meta:
        ordering = ['-created']


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
            )
        ]
