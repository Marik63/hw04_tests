from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PaginatorTest(TestCase):
    """Класс тестирования паджинатора."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='paginator')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='paginator_test_slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            [
                Post(
                    text=f'{i} - Тестовый пост с группой.',
                    author=cls.user,
                    group=cls.group,
                )
            for i in range(15)
            ]
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorTest.user)

    def test_paginator_first_page_records(self):
        """Тестируем первую страницу паджинатора."""
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
                self.assertEqual(len(response.context[obj]), 10)

    def test_paginator_second_page_records(self):
        """Тестируем вторую страницу паджинатора."""
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
                self.assertEqual(len(response.context[obj]), 5)
