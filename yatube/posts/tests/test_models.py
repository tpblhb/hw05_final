from django.test import TestCase
from mixer.backend.django import mixer
from strenum import StrEnum

from core.utils import truncatechars
from posts.models import Comment, Group, Post


class PostModelTest(TestCase):
    class Fields(StrEnum):
        text = 'text'
        author = 'author'
        group = 'group'
        image = 'image'

    def test_model_have_correct_str(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = mixer.blend(Post)
        self.assertEqual(
            str(post),
            truncatechars(post.text),
        )

    def test_model_have_correct_verboses(self):
        """Проверяем, что у модели Post корректно работают verbose_name."""
        verboses = (
            (self.Fields.text, 'текст'),
            (self.Fields.author, 'автор'),
            (self.Fields.group, 'группа'),
            (self.Fields.image, 'картинка'),
        )
        for field, verbose in verboses:
            with self.subTest(field=field, verbose=verbose):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    verbose,
                )

    def test_model_have_correct_help_text(self):
        """Проверяем, что у модели Post корректно работают help_text."""
        helptexts = (
            (self.Fields.text, 'введите текст поста'),
            (self.Fields.group, 'выберите группу'),
        )
        for field, verbose in helptexts:
            with self.subTest(field=field, verbose=verbose):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    verbose,
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend(Group)

    def test_model_have_correct_str(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(
            str(self.group),
            truncatechars(self.group.title),
        )


class CommentModelTest(TestCase):
    class Fields(StrEnum):
        text = 'text'
        author = 'author'
        post = 'post'

    def test_model_have_correct_str(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = mixer.blend(Comment)
        self.assertEqual(
            str(comment),
            f'{comment.text}, автор: {comment.author}',
        )

    def test_model_have_correct_verboses(self):
        """Проверяем, что у модели Comment корректно работают verbose_name."""
        verboses = (
            (self.Fields.text, 'текст'),
            (self.Fields.author, 'автор'),
        )
        for field, verbose in verboses:
            with self.subTest(field=field, verbose=verbose):
                self.assertEqual(
                    Comment._meta.get_field(field).verbose_name,
                    verbose,
                )

    def test_model_have_correct_help_text(self):
        """Проверяем, что у модели Comment корректно работают help_text."""
        helptexts = (
            (self.Fields.text, 'введите текст поста'),
            (self.Fields.post, 'комментарий к посту'),
        )
        for field, verbose in helptexts:
            with self.subTest(field=field, verbose=verbose):
                self.assertEqual(
                    Comment._meta.get_field(field).help_text,
                    verbose,
                )
