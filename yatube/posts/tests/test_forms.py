import shutil

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Group, Post, User
from posts.tests.common import image


@override_settings(MEDIA_ROOT=settings.MEDIATESTS)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend(Group)
        cls.user = mixer.blend(User)

        cls.anon = Client()
        cls.auth = Client()

        cls.auth.force_login(cls.user)

    def tearDown(self):
        shutil.rmtree(settings.MEDIATESTS, ignore_errors=True)

    def test_post_create(self):
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
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(post.group, self.group)
        self.assertTrue(post.image.name.endswith(image().name))

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post = mixer.blend(Post, author=self.user)
        self.assertEqual(Post.objects.count(), 1)
        response = self.auth.post(
            reverse(
                'posts:post_edit',
                args={post.pk},
            ),
            {
                'text': 'Изменённый тестовый пост',
                'group': self.group.id,
                'image': image('test2.gif'),
            },
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args={post.pk},
            ),
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, 'Изменённый тестовый пост')
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertTrue(post.image.name, 'posts/test2.gif')

    def test_create_post_guest(self):
        Client().post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_edit_post_not_author(self):
        post = mixer.blend(Post)
        self.assertEqual(Post.objects.count(), 1)
        Client().post(
            reverse(
                'posts:post_edit',
                args={post.pk},
            ),
            {
                'text': 'Изменённый тестовый пост',
            },
        )
        post.refresh_from_db()
        self.assertNotEqual(post.text, 'Изменённый тестовый пост')

    def test_auth_comment(self):
        post = mixer.blend(Post)
        self.auth.post(
            reverse(
                'posts:add_comment',
                args={post.id},
            ),
            {'text': 'Тестовый комментарий'},
            follow=True,
        )
        self.assertTrue(
            Comment.objects.filter(text='Тестовый комментарий').exists()
        )

    def test_anon_comment(self):
        post = mixer.blend(Post)
        Client().post(
            reverse(
                'posts:add_comment',
                args={post.id},
            ),
            {'text': 'Тестовый комментарий'},
            follow=True,
        )
        self.assertFalse(
            Comment.objects.filter(text='Тестовый комментарий').exists()
        )
