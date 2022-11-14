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
        cls.auth = Client()
        cls.auth.force_login(cls.user)

        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )

        cls.urls = {
            'group_list': reverse(
                'posts:group_list',
                args=(cls.group.slug,),
            ),
            'index': reverse('posts:index'),
            'profile': reverse(
                'posts:profile',
                args=(cls.author.username,),
            ),
            'post_detail': reverse(
                'posts:post_detail',
                args=(cls.post.id,),
            ),
            'post_edit': reverse(
                'posts:post_edit',
                args=(cls.post.id,),
            ),
            'post_create': reverse('posts:post_create'),
            'follow_index': reverse('posts:follow_index'),
            '/missing/': '/missing/',
        }

    def test_http_statuses(self) -> None:
        httpstatuses = (
            (self.urls.get('index'), HTTPStatus.OK, Client()),
            (self.urls.get('post_create'), HTTPStatus.FOUND, Client()),
            (self.urls.get('post_create'), HTTPStatus.OK, self.auth),
            (self.urls.get('follow_index'), HTTPStatus.FOUND, Client()),
            (self.urls.get('follow_index'), HTTPStatus.OK, self.auth),
            (
                self.urls.get('group_list'),
                HTTPStatus.OK,
                Client(),
            ),
            (self.urls.get('/missing/'), HTTPStatus.NOT_FOUND, Client()),
            (
                self.urls.get('post_detail'),
                HTTPStatus.OK,
                Client(),
            ),
            (
                self.urls.get('post_edit'),
                HTTPStatus.OK,
                self.authorized_author,
            ),
            (
                self.urls.get('post_edit'),
                HTTPStatus.FOUND,
                Client(),
            ),
            (
                self.urls.get('post_edit'),
                HTTPStatus.FOUND,
                self.auth,
            ),
            (
                self.urls.get('profile'),
                HTTPStatus.OK,
                Client(),
            ),
        )

        for adress, status, client in httpstatuses:
            with self.subTest(adress=adress):
                self.assertEqual(client.get(adress).status_code, status)
                self.assertEqual(
                    client.get(
                        redirect_to_login(self.urls.get(adress)).url,
                    ).status_code,
                    HTTPStatus.OK,
                )

    def test_templates(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates = (
            (self.urls.get('index'), 'posts/index.html', Client()),
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.auth,
            ),
            (self.urls.get('follow_index'), 'posts/follow.html', self.auth),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                Client(),
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.authorized_author,
            ),
            (
                self.urls.get('group_list'),
                'posts/group_list.html',
                Client(),
            ),
            (
                self.urls.get('profile'),
                'posts/profile.html',
                Client(),
            ),
        )

        for adress, template, client in templates:
            with self.subTest(adress=adress):
                self.assertTemplateUsed(client.get(adress), template)

    def test_redirects(self) -> None:
        redirects = (
            (
                self.urls.get('post_create'),
                redirect_to_login(self.urls.get('post_create')).url,
                Client(),
            ),
            (
                self.urls.get('post_edit'),
                redirect_to_login(
                    self.urls.get('post_edit'),
                ).url,
                Client(),
            ),
            (
                self.urls.get('post_edit'),
                self.urls.get('post_detail'),
                self.auth,
            ),
        )

        for adress, redirect, client in redirects:
            with self.subTest(adress=adress):
                self.assertRedirects(client.get(adress), redirect)
