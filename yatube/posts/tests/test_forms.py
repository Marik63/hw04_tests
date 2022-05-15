from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


User = get_user_model()


class PostsFormsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create(
            username='test_user',
        )
        # Создаем группу
        cls.group = Group.objects.create(
            title='Test group 1',
            slug='test_group_slug',
            description='Test group 1 description'
        )
        # Создадим запись в БД
        cls.post = Post.objects.create(
            text='Test post 1 text.',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self) -> None:
        self.user = PostsFormsTestCase.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_valid_post(self):
        """
        Проверяем при отправке валидной формы со страницы создания поста
        reverse('posts:post_create') создаётся новая запись в базе данных.
        """
        # Подсчитаем количество записей в Post
        post = Post.objects.latest('pub_date')
        count = Post.objects.count()
        form_data = {
            'text': 'Test post 1 text.',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        post_last = {
            post.text: form_data['text'],
            post.group.id: form_data['group'],
            post.author: PostsFormsTestCase.user
        }
        for date, value in post_last.items():
            with self.subTest(date=date):
                self.assertEqual(date, value)

    def test_edit_valid_post(self):
        """
        Проверяем при отправке валидной формы со страницы редактирования
        поста reverse('posts:post_edit') меняется запись в базе данных.
        """
        post = Post.objects.latest('pub_date')
        form_data = {
            'text': 'Test post 1 text.',
            'group': self.group.id,
        }
        post_last = {
            post.text: form_data['text'],
            post.group.id: form_data['group'],
            post.author: PostsFormsTestCase.user,
        }
        for date, value in post_last.items():
            with self.subTest(date=date):
                self.assertEqual(date, value)