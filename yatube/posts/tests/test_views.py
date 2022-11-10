import shutil

from django import forms
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Follow, Group, Post, User
from yatube.settings import MEDIATESTS

from .common import image


@override_settings(MEDIA_ROOT=MEDIATESTS)
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
        cls.index = (
            'posts:index',
            'posts/index.html',
            None,
        )
        cls.group_list = (
            'posts:group_list',
            'posts/group_list.html',
            {'slug': cls.group.slug},
        )
        cls.profile = (
            'posts:profile',
            'posts/profile.html',
            {'username': cls.anon},
        )
        cls.post_detail = (
            'posts:post_detail',
            'posts/post_detail.html',
            {'id': cls.post.id},
        )
        cls.post_create = (
            'posts:post_create',
            'posts/create_post.html',
            None,
        )
        cls.post_edit = (
            'posts:post_edit',
            'posts/create_post.html',
            {'id': cls.post.id},
        )
        cls.all_pages = [
            cls.index,
            cls.group_list,
            cls.post_detail,
            cls.profile,
            cls.post_create,
            cls.post_edit,
        ]
        cls.paginated = [
            cls.index,
            cls.group_list,
            cls.profile,
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIATESTS, ignore_errors=True)

    def test_pages_uses_correct_templates(self):
        """URL-адреса используют корректные шаблоны."""
        for address, template, kwargs in self.all_pages:
            with self.subTest(reverse_name=address):
                response = self.auth.get(
                    reverse(address, kwargs=kwargs),
                )
                self.assertTemplateUsed(response, template)

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
        for name, params, kwargs in self.paginated:
            with self.subTest(name=name, params=params):
                response = self.auth.get(
                    reverse(name, kwargs=kwargs),
                )
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.auth.get(
                    reverse(name, kwargs=kwargs) + '?page=2',
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
