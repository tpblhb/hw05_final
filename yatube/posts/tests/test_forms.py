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
        cls.user = mixer.blend(User)

        cls.anon = Client()
        cls.auth = Client()

        cls.auth.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIATESTS, ignore_errors=True)

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
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
            image=image(),
        )
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
            f'/posts/{post.pk}/',
        )
        self.assertEqual(post.author, Post.objects.get(id=post.id).author)
        self.assertTrue(
            Post.objects.get(id=post.id).image.name.endswith(
                image('test2.gif').name,
            ),
        )
        self.assertEqual(Post.objects.get(id=post.id).group, self.group)
        self.assertEqual(
            Post.objects.get(id=post.id).text,
            'Изменённый тестовый пост',
        )

    def test_create_post_guest(self):
        self.anon.post(
            reverse('posts:post_create'),
            data={
                'text': 'Тестовый пост',
                'group': self.group.id,
                'image': image(),
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_edit_post_not_author(self):
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
            image=image(),
        )
        self.assertEqual(Post.objects.count(), 1)
        self.anon.post(
            reverse(
                'posts:post_edit',
                args={post.pk},
            ),
            {
                'text': 'Изменённый тестовый пост',
            },
        )
        self.assertEqual(Post.objects.get(id=post.id).text, 'Тестовый пост')
