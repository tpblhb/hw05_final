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
        cls.user, cls.author_user = mixer.cycle(2).blend(User)
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, author=cls.author_user)

        cls.author = Client()
        cls.auth = Client()
        cls.author.force_login(cls.author_user)
        cls.auth.force_login(cls.user)

        cls.urls = {
            'add_comment': reverse(
                'posts:add_comment',
                args=(cls.post.id,),
            ),
            'follow_index': reverse('posts:follow_index'),
            'group_list': reverse(
                'posts:group_list',
                args=(cls.group.slug,),
            ),
            'index': reverse('posts:index'),
            '/missing/': '/missing/',
            'post_create': reverse('posts:post_create'),
            'post_detail': reverse(
                'posts:post_detail',
                args=(cls.post.id,),
            ),
            'post_edit': reverse(
                'posts:post_edit',
                args=(cls.post.id,),
            ),
            'profile': reverse(
                'posts:profile',
                args=(cls.author_user.username,),
            ),
        }

    def test_http_statuses(self) -> None:
        httpstatuses = (
            (self.urls.get('add_comment'), HTTPStatus.FOUND, Client()),
            (self.urls.get('add_comment'), HTTPStatus.FOUND, self.auth),
            (self.urls.get('follow_index'), HTTPStatus.FOUND, Client()),
            (self.urls.get('follow_index'), HTTPStatus.OK, self.auth),
            (
                self.urls.get('group_list'),
                HTTPStatus.OK,
                Client(),
            ),
            (self.urls.get('index'), HTTPStatus.OK, Client()),
            (self.urls.get('/missing/'), HTTPStatus.NOT_FOUND, Client()),
            (self.urls.get('post_create'), HTTPStatus.FOUND, Client()),
            (self.urls.get('post_create'), HTTPStatus.OK, self.auth),
            (
                self.urls.get('post_detail'),
                HTTPStatus.OK,
                Client(),
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
                self.urls.get('post_edit'),
                HTTPStatus.OK,
                self.author,
            ),
            (
                self.urls.get('profile'),
                HTTPStatus.OK,
                Client(),
            ),
        )

        for adress, status, client in httpstatuses:
            with self.subTest(adress=adress, status=status, client=client):
                self.assertEqual(client.get(adress).status_code, status)

    def test_templates(self) -> None:
        templates = (
            (self.urls.get('follow_index'), 'posts/follow.html', self.auth),
            (
                self.urls.get('group_list'),
                'posts/group_list.html',
                Client(),
            ),
            (self.urls.get('index'), 'posts/index.html', Client()),
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.auth,
            ),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                Client(),
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.author,
            ),
            (
                self.urls.get('profile'),
                'posts/profile.html',
                Client(),
            ),
        )

        for adress, template, client in templates:
            with self.subTest(adress=adress, template=template, client=client):
                self.assertTemplateUsed(client.get(adress), template)

    def test_redirects(self) -> None:
        redirects = (
            (
                self.urls.get('add_comment'),
                self.urls.get('post_detail'),
                self.auth,
            ),
            (
                self.urls.get('post_create'),
                redirect_to_login(self.urls.get('post_create')).url,
                Client(),
            ),
            (
                self.urls.get('post_edit'),
                self.urls.get('post_detail'),
                self.auth,
            ),
            (
                self.urls.get('post_edit'),
                redirect_to_login(
                    self.urls.get('post_edit'),
                ).url,
                Client(),
            ),
        )

        for adress, redirect, client in redirects:
            with self.subTest(adress=adress, redirect=redirect, client=client):
                self.assertRedirects(client.get(adress), redirect)
