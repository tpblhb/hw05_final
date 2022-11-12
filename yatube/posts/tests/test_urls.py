from http import HTTPStatus

from django.contrib.auth.views import redirect_to_login
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='user')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.anon = Client()
        cls.auth = Client()
        cls.auth.force_login(cls.user)

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=mixer.blend(Group),
        )

        cls.urls = {
            f'/group/{cls.post.group.slug}/': reverse(
                'posts:group_list',
                args=(cls.post.group.slug,),
            ),
            '/': reverse('posts:index'),
            f'/profile/{cls.author.username}/': reverse(
                'posts:profile',
                args=(cls.author.username,),
            ),
            f'/posts/{cls.post.id}/': reverse(
                'posts:post_detail',
                args=(cls.post.id,),
            ),
            f'/posts/{cls.post.id}/edit/': reverse(
                'posts:post_edit',
                args=(cls.post.id,),
            ),
            'create/': reverse('posts:post_create'),
            'follow/': reverse('posts:follow_index'),
            '/missing/': '/missing/',
        }

    def test_http_statuses(self) -> None:
        httpstatuses = (
            (self.urls.get('/'), HTTPStatus.OK, self.anon),
            (self.urls.get('create/'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('create/'), HTTPStatus.OK, self.auth),
            (self.urls.get('follow/'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('follow/'), HTTPStatus.OK, self.auth),
            (
                self.urls.get(f'/group/{self.post.group.slug}/'),
                HTTPStatus.OK,
                self.anon,
            ),
            (self.urls.get('/missing/'), HTTPStatus.NOT_FOUND, self.anon),
            (
                self.urls.get(f'/posts/{self.post.id}/'),
                HTTPStatus.OK,
                self.anon,
            ),
            (
                self.urls.get(f'/posts/{self.post.id}/edit/'),
                HTTPStatus.OK,
                self.authorized_author,
            ),
            (
                self.urls.get(f'/posts/{self.post.id}/edit/'),
                HTTPStatus.FOUND,
                self.anon,
            ),
            (
                self.urls.get(f'/posts/{self.post.id}/edit/'),
                HTTPStatus.FOUND,
                self.auth,
            ),
            (
                self.urls.get(f'/profile/{self.author.username}/'),
                HTTPStatus.OK,
                self.anon,
            ),
        )

        for adress, status, client in httpstatuses:
            with self.subTest(adress=adress):
                self.assertEqual(client.get(adress).status_code, status)
                self.assertEqual(
                    client.get(f'/auth/login/?next={adress}').status_code,
                    HTTPStatus.OK,
                )

    def test_templates(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates = (
            (self.urls.get('/'), 'posts/index.html', self.anon),
            (self.urls.get('create/'), 'posts/create_post.html', self.auth),
            (self.urls.get('follow/'), 'posts/follow.html', self.auth),
            (
                self.urls.get(f'/posts/{self.post.id}/'),
                'posts/post_detail.html',
                self.anon,
            ),
            (
                self.urls.get(f'/posts/{self.post.id}/edit/'),
                'posts/create_post.html',
                self.authorized_author,
            ),
            (
                self.urls.get(f'/group/{self.post.group.slug}/'),
                'posts/group_list.html',
                self.anon,
            ),
            (
                self.urls.get(f'/profile/{self.author.username}/'),
                'posts/profile.html',
                self.anon,
            ),
        )

        for adress, template, client in templates:
            with self.subTest(adress=adress):
                self.assertTemplateUsed(client.get(adress), template)

    def test_redirects(self) -> None:
        redirects = (
            (
                self.urls.get('create/'),
                redirect_to_login(self.urls.get('create/')).url,
                self.anon,
            ),
            (
                self.urls.get(f'/posts/{self.post.id}/edit/'),
                redirect_to_login(
                    self.urls.get(f'/posts/{self.post.id}/edit/'),
                ).url,
                self.anon,
            ),
            (
                self.urls.get(f'/posts/{self.post.id}/edit/'),
                f'/posts/{self.post.id}/',
                self.auth,
            ),
        )

        for adress, redirect, client in redirects:
            with self.subTest(adress=adress):
                self.assertRedirects(client.get(adress), redirect)
