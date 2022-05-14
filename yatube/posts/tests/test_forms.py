import shutil
import tempfile
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, override_settings, TestCase
from django.urls import reverse


from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
            text='Test post 1 text. It must be at least 20 symbols.',
            author=cls.user,
            group=cls.group,
            pub_date=Post.pub_date
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
        count = Post.objects.count()
        form_data = {
            'text': 'Test post 2 text. It must be at least 20 symbols.',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_1 = Post.objects.get(id=self.group.id)
        author_1 = User.objects.get(username='test_user')
        group_1 = Group.objects.get(title='Test group 1')
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(post_1.text, 'Test post 1 text. It must be at least 20 symbols.')
        self.assertEqual(author_1.username, 'test_user')
        self.assertEqual(group_1.title, 'Test group 1')
        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_edit_valid_post(self):
        """
        Проверяем при отправке валидной формы со страницы редактирования
        поста reverse('posts:post_edit') меняется запись в базе данных.
        """
        post = PostsFormsTestCase.post
        form_data = {
            'text': 'Test post 2 text. We change this post',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{post.id}'}),
            data=form_data,
            follow=True,
        )
        author_2 = User.objects.get(username='test_user')
        group_2 = Group.objects.get(title='Test group 1')
        self.assertEqual(
            Post.objects.get(
                id=post.id).text, 'Test post 2 text. We change this post')
        self.assertEqual(author_2.username, 'test_user')
        self.assertEqual(group_2.title, 'Test group 1')

        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.context.get('post').text, form_data['text'])
        self.assertEqual(
            response.context.get('post').group.id,
            form_data['group']
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
