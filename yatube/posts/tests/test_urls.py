from http import HTTPStatus

from django.test import Client, TestCase
from mixer.backend.django import mixer

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.author = User.objects.create_user(username='author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.user = User.objects.create_user(username='user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=mixer.blend(Group),
        )
        cls.post_url = f'/{cls.author.username}/{cls.post.id}/'
        cls.public_urls = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.post.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.author.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post.id}/', 'posts/post_detail.html'),
        )
        cls.private_urls = (
            ('/create/', 'posts/create_post.html'),
            (f'/posts/{cls.post.id}/edit/', 'posts/create_post.html'),
            ('/follow/', 'posts/follow.html'),
        )

    def urls_uses_correct_template(self, data_url, client, status):
        for url, template in data_url:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template)

    def test_urls(self):
        """URL-адреса используют соответствующие шаблоны."""
        self.urls_uses_correct_template(
            self.public_urls,
            self.client,
            HTTPStatus.OK,
        )
        self.urls_uses_correct_template(
            self.private_urls,
            self.authorized_author,
            HTTPStatus.OK,
        )

    def test_urls_template_authorized(self):
        """Шаблон create редиректит неавторизованного пользователя"""
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_url_templates_author(self):
        """Шаблон edit редиректит не автора поста"""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/',
            follow=True,
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_404(self):
        """Проверка несуществующей страницы"""
        response = self.client.get('/posts/200/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_follow_user(self):
        response = self.authorized_author.get("/follow/")
        self.assertTemplateUsed(response, "posts/follow.html")
        self.assertEqual(response.status_code, 200)
