from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PaginatorTest(TestCase):
    """Класс тестирования паджинатора"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POSTS_NUMBER = 29  # from 21 to 29
        cls.PAGE_POSTS = 10
        cls.user = User.objects.create_user(username='paginator')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='paginator_test_slug',
            description='Тестовое описание',
        )
        for i in range(cls.POSTS_NUMBER):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'Тестовый пост для проверки. Номер: {i}',
            )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorTest.user)

    def test_paginator_first_page_records(self):
        """Тестируем первую страницу паджинатора"""
        paginator_pages = {
            reverse('posts:index'): 'page_obj',
            reverse('posts:group_list', kwargs={
                'slug': 'paginator_test_slug'}): 'page_obj',
            reverse('posts:profile', kwargs={'username': 'paginator'}):
                'page_obj',
        }
        for reverse_name, obj in paginator_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context[obj]), self.PAGE_POSTS)

    def test_paginator_second_page_records(self):
        """Тестируем вторую страницу паджинатора"""
        paginator_pages = {
            reverse('posts:index') + '?page=2': 'page_obj',
            reverse('posts:group_list',
                    kwargs={'slug': 'paginator_test_slug'})
            + '?page=2': 'page_obj',
            reverse('posts:profile',
                    kwargs={'username': 'paginator'}) + '?page=2': 'page_obj',
        }
        for reverse_name, obj in paginator_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context[obj]), self.PAGE_POSTS)

    def test_paginator_third_page_records(self):
        """Тестируем третью страницу паджинатора"""
        paginator_pages = {
            reverse('posts:index') + '?page=3': 'page_obj',
            reverse('posts:group_list',
                    kwargs={'slug': 'paginator_test_slug'})
            + '?page=3': 'page_obj',
            reverse('posts:profile',
                    kwargs={'username': 'paginator'}) + '?page=3': 'page_obj',
        }
        for reverse_name, obj in paginator_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context[obj]),
                                 self.POSTS_NUMBER % self.PAGE_POSTS)
