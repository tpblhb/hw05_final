from django.test import TestCase
from mixer.backend.django import mixer
from strenum import StrEnum

from core.utils import truncatechars
from posts.models import MAX_TITLE_LENGTH, Group, Post, User


class Fields(StrEnum):
    text = 'text'
    author = 'author'
    group = 'group'


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
            truncatechars(self.post.text),
        )

    def test_post_model_have_correct_verboses(self):
        """Проверяем, что у модели Post корректно работают verbose_name."""
        verboses = (
            Fields.text,
            Fields.author,
            Fields.group,
        )
        self.assertEqual(
            self.post._meta.get_field(verboses[0]).verbose_name,
            'текст',
        )
        self.assertEqual(
            self.post._meta.get_field(verboses[1]).verbose_name,
            'автор',
        )
        self.assertEqual(
            self.post._meta.get_field(verboses[2]).verbose_name,
            'группа',
        )

    def test_post_model_have_correct_help_text(self):
        """Проверяем, что у модели Post корректно работают help_text."""
        helptexts = (
            Fields.text,
            Fields.group,
        )
        self.assertEqual(
            self.post._meta.get_field(helptexts[0]).help_text,
            'введите текст поста',
        )
        self.assertEqual(
            self.post._meta.get_field(helptexts[1]).help_text,
            'выберите группу',
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
