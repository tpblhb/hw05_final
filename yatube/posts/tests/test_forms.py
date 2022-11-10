import shutil

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post, User
from yatube.settings import MEDIATESTS

from .common import image


@override_settings(MEDIA_ROOT=MEDIATESTS)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend(Group)
        cls.user = User.objects.create_user(username='testname')
        cls.auth = Client()
        cls.auth.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIATESTS, ignore_errors=True)

    def test_post_create_form(self):
        """Создание нового Post."""
        self.assertEqual(Post.objects.count(), 0)
        response = self.auth.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.id,
                'image': image(),
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,)),
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertTrue(Post.objects.filter(text='Тестовый пост').exists())
        self.assertTrue(Post.objects.filter(group=self.group.id).exists())
        self.assertTrue(
            Post.objects.filter(image__contains='test.gif').exists(),
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        response = self.auth.post(
            reverse(
                'posts:post_edit',
                args=(f'{self.post.pk}',),
            ),
            {
                'text': 'Изменённый тестовый пост',
                'group': self.group.id,
            },
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post.pk}/',
        )
        response_post_detail = self.auth.get(
            reverse(
                'posts:post_detail',
                args=(f'{self.post.pk}',),
            ),
        )
        self.assertContains(response_post_detail, 'Изменённый тестовый пост')
