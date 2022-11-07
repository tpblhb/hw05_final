from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend(Group)
        cls.user = User.objects.create_user(username='testname')
        cls.auth = Client()
        cls.auth.force_login(cls.user)

    def setUp(self):
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='test.gif',
            content=self.small_gif,
            content_type='image/gif',
        )

    def test_post_create_form(self):
        """Создание нового Post."""
        self.assertEqual(Post.objects.count(), 0)
        response = self.auth.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.id,
                'image': self.uploaded,
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,)),
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост',
                group=self.group.id,
                image__contains='posts/test.gif',
            ).exists()
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
