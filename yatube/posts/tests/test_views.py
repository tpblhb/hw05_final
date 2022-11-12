import shutil

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Follow, Group, Post, User
from posts.tests.common import image


@override_settings(MEDIA_ROOT=settings.MEDIATESTS)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.anon = User.objects.create_user(username='Test User')
        cls.anon2 = User.objects.create_user(username='Test User2')
        cls.anon3 = User.objects.create_user(username='Test User3')
        cls.auth = Client()
        cls.auth.force_login(cls.anon)
        cls.auth2 = Client()
        cls.auth2.force_login(cls.anon2)
        cls.auth3 = Client()
        cls.auth3.force_login(cls.anon3)
        Follow.objects.create(user=cls.anon, author=cls.anon3)
        cls.group = mixer.blend(Group)
        post = (
            Post(
                author=cls.anon,
                group=cls.group,
                text=f'Текст поста {post_number+1}',
                image=image(),
            )
            for post_number in range(15)
        )
        Post.objects.bulk_create(post)
        cls.post = Post.objects.first()
        cls.all_pages = {
            '/': reverse('posts:index'),
            'create/': reverse('posts:post_create'),
            f'/group/{cls.post.group.slug}/': reverse(
                'posts:group_list',
                args=(cls.post.group.slug,),
            ),
            f'/posts/{cls.post.id}/': reverse(
                'posts:post_detail',
                args=(cls.post.id,),
            ),
            f'/posts/{cls.post.id}/edit/': reverse(
                'posts:post_edit',
                args=(cls.post.id,),
            ),
            f'/profile/{cls.anon.username}/': reverse(
                'posts:profile',
                args=(cls.anon.username,),
            ),
        }
        cls.paginated = {
            '/': reverse('posts:index'),
            f'/group/{cls.post.group.slug}/': reverse(
                'posts:group_list',
                args=(cls.post.group.slug,),
            ),
            f'/profile/{cls.anon.username}/': reverse(
                'posts:profile',
                args=(cls.anon.username,),
            ),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIATESTS, ignore_errors=True)

    def test_pages_uses_correct_templates(self):
        """URL-адреса используют корректные шаблоны."""
        templates = (
            (self.all_pages.get('/'), 'posts/index.html', self.auth),
            (
                self.all_pages.get('create/'),
                'posts/create_post.html',
                self.auth,
            ),
            (
                self.all_pages.get(f'/group/{self.post.group.slug}/'),
                'posts/group_list.html',
                self.auth,
            ),
            (
                self.all_pages.get(f'/posts/{self.post.id}/'),
                'posts/post_detail.html',
                self.auth,
            ),
            (
                self.all_pages.get(f'/posts/{self.post.id}/edit/'),
                'posts/create_post.html',
                self.auth,
            ),
            (
                self.all_pages.get(f'/profile/{self.anon.username}/'),
                'posts/profile.html',
                self.auth,
            ),
        )

        for adress, template, client in templates:
            with self.subTest(adress=adress):
                self.assertTemplateUsed(client.get(adress), template)

    def test_index_page_uses_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.auth.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0],
            self.post,
        )

    def test_group_list_uses_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.auth.get(
            reverse('posts:group_list', args={self.group.slug}),
        )
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(
            response.context['page_obj'][0],
            self.group.posts.first(),
        )

    def test_profile_uses_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.auth.get(
            reverse('posts:profile', args={self.anon}),
        )
        self.assertEqual(response.context['author'], self.anon)
        self.assertEqual(
            response.context['page_obj'][0],
            self.anon.posts.first(),
        )

    def test_group_list_index_profile_paginator_work(self):
        """Пагинатор работает в group_list, index и profile."""
        templates = (
            (
                'posts:group_list',
                'posts/group_list.html',
                {'slug': self.group.slug},
            ),
            (
                'posts:index',
                'posts/index.html',
                None,
            ),
            (
                'posts:profile',
                'posts/profile.html',
                {'username': self.anon},
            ),
        )

        for adress, params, kwargs in templates:
            with self.subTest(adress=adress, params=params):
                response = self.auth.get(
                    reverse(adress, kwargs=kwargs),
                )
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.auth.get(
                    reverse(adress, kwargs=kwargs) + '?page=2',
                )
                self.assertEqual(len(response.context['page_obj']), 5)

    def test_post_detail_uses_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.auth.get(
            reverse('posts:post_detail', args={self.post.id}),
        )
        self.assertEqual(response.context.get('post').id, self.post.id)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(
            response.context.get('post').author,
            self.post.author,
        )
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_post_create_uses_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.auth.get(
            reverse('posts:post_create'),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_uses_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.auth.get(
            reverse(
                'posts:post_edit',
                args={self.post.id},
            ),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_cached(self):
        """Главная страница кэшируется"""
        response = self.auth.get(reverse('posts:index'))
        post = Post.objects.create(
            text='Проверяем кэширование страницы',
            author=self.anon,
        )
        cached = self.auth.get(reverse('posts:index'))
        post.delete()
        response = self.auth.get(reverse('posts:index'))
        self.assertEqual(cached.content, response.content)
        cache.clear()
        response = self.auth.get(reverse('posts:index'))
        self.assertNotEqual(cached.content, response.content)

    def test_auth_follow_and_unfollow(self):
        self.auth2.get(
            reverse('posts:profile_follow', args={self.anon.username}),
        )
        self.assertTrue(
            Follow.objects.filter(author=self.anon, user=self.anon2).exists(),
        )
        self.auth2.get(
            reverse(
                'posts:profile_unfollow',
                args={self.anon.username},
            ),
        )
        self.assertFalse(
            Follow.objects.filter(author=self.anon, user=self.anon2).exists(),
        )

    def test_post_show_for_follower_and_not_show_for_unfollower(self):
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.anon3,
        )
        response = self.auth.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)
        response = self.auth2.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
