from django.test import TestCase
from mixer.backend.django import mixer

from posts.models import MAX_TEXT_LENGTH, MAX_TITLE_LENGTH, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_post_model_have_correct_str(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = self.post
        field_verboses = {
            'text': 'текст',
            'pub_date': 'дата публикации',
            'author': 'автор',
            'group': 'группа',
        }
        field_help_texts = {
            'text': 'введите текст поста',
            'group': 'выберите группу',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name,
                    expected,
                )
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text,
                    expected,
                )
        self.assertEqual(str(post), post.text[:MAX_TEXT_LENGTH])

    def test_group_model_have_correct_str(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = self.group
        self.assertEqual(
            str(group),
            group.title[:MAX_TITLE_LENGTH] + '...'
            if len(group.title) > MAX_TITLE_LENGTH
            else group.title,
        )
