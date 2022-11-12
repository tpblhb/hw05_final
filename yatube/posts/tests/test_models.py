from django.test import TestCase
from mixer.backend.django import mixer
from strenum import StrEnum

from core.utils import truncatechars
from posts.models import MAX_TEXT_LENGTH, MAX_TITLE_LENGTH, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_post_model_have_correct_str(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        self.assertEqual(
            str(self.post),
            truncatechars(self.post.text, MAX_TEXT_LENGTH),
        )

    def test_post_model_have_correct_verboses(self):
        """Проверяем, что у модели Post корректно работают verbose_name."""

        class Fields(StrEnum):
            text = 'text'
            author = 'author'
            group = 'group'

        verboses = {
            Fields.text: 'текст',
            Fields.author: 'автор',
            Fields.group: 'группа',
        }
        for value, expected in verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name,
                    expected,
                )

    def test_post_model_have_correct_help_text(self):
        """Проверяем, что у модели Post корректно работают help_text."""

        class Fields(StrEnum):
            text = 'text'
            group = 'group'

        helptexts = {
            Fields.text: 'введите текст поста',
            Fields.group: 'выберите группу',
        }
        for value, expected in helptexts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text,
                    expected,
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend(Group)

    def test_group_model_have_correct_str(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(
            str(self.group),
            truncatechars(self.group.title, MAX_TITLE_LENGTH),
        )
