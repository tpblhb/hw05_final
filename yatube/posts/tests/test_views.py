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
        cls.author = mixer.blend(User)
        cls.anon = mixer.blend(User)
        Follow.objects.create(user=cls.author, author=cls.anon)
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Текст поста',
            image=image(),
        )

        cls.auth = Client()
        cls.auth2 = Client()

        cls.auth.force_login(cls.author)
        cls.auth2.force_login(cls.anon)

        cls.paginated = (
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug},
            ),
            reverse(
                'posts:index',
                kwargs=None,
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.author},
            ),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIATESTS, ignore_errors=True)

    def test_index_page_uses_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.auth.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0].author,
            self.post.author,
        )
        self.assertEqual(
            response.context['page_obj'][0].group,
            self.post.group,
        )
        self.assertEqual(
            response.context['page_obj'][0].text,
            self.post.text,
        )
        self.assertEqual(
            response.context['page_obj'][0].image,
            self.post.image,
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
            reverse('posts:profile', args={self.author}),
        )
        self.assertEqual(response.context['author'], self.author)
        self.assertEqual(
            response.context['page_obj'][0],
            self.author.posts.first(),
        )

    def test_group_list_index_profile_paginator_work(self):
        """Пагинатор работает в group_list, index и profile."""
        post = (
            Post(
                author=self.author,
                group=self.group,
                text=f'Текст поста {post_number+1}',
                image=image(),
            )
            for post_number in range(15)
        )
        Post.objects.bulk_create(post)

        for adress in self.paginated:
            with self.subTest(adress=adress):
                response = self.auth.get(adress)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.auth.get(adress + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 6)

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
            author=self.author,
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
            reverse('posts:profile_follow', args={self.author.username}),
        )
        self.assertTrue(
            Follow.objects.filter(author=self.author, user=self.anon).exists(),
        )
        self.auth2.get(
            reverse(
                'posts:profile_unfollow',
                args={self.author.username},
            ),
        )
        self.assertFalse(
            Follow.objects.filter(author=self.author, user=self.anon).exists(),
        )

    def test_post_show_for_follower_and_not_show_for_unfollower(self):
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.anon,
        )
        response = self.auth.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)
        response = self.auth2.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
