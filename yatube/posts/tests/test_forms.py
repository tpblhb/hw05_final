import shutil

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post, User
from posts.tests.common import image


@override_settings(MEDIA_ROOT=settings.MEDIATESTS)
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
        shutil.rmtree(settings.MEDIATESTS, ignore_errors=True)

    def test_post_create_form(self):
        """Создание нового Post."""
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
        post = Post.objects.get()
        self.assertEqual(
            (
                post.text,
                post.group.id,
                post.image.name,
            ),
            (
                'Тестовый пост',
                self.group.id,
                f'posts/{image().name}',
            ),
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
            image=image('test2.gif'),
        )
        response = self.auth.post(
            reverse(
                'posts:post_edit',
                args=(f'{self.post.pk}',),
            ),
            {
                'text': 'Изменённый тестовый пост',
                'group': self.group.id,
                'image': image('test3.gif'),
            },
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post.pk}/',
        )
        response_post_detail = Post.objects.get(id=self.post.id)
        self.assertEqual(self.post.author, response_post_detail.author)
        self.assertEqual(response_post_detail.image.name, 'posts/test3.gif')
        self.assertEqual(response_post_detail.group.id, self.group.id)
        self.assertEqual(self.post.pub_date, response_post_detail.pub_date)
        self.assertEqual(response_post_detail.text, 'Изменённый тестовый пост')
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args={self.post.id}),
        )
        self.assertEqual(Post.objects.count(), 1)
