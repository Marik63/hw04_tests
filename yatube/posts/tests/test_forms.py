import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings, tag
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create(
            username='test_user',
        )
        cls.group = Group.objects.create(
            title='Test group 1',
            slug='test_group_slug',
            description='Test group 1 description'
        )
        cls.group_image = Group.objects.create(
            title='Тестовая группа для постов с изображением',
            slug='posts_test_image_slug',
            description='Тестовое описание с изображением',
        )
        cls.post = Post.objects.create(
            text='Test post 1 text. It must be at least 20 symbols.',
            author=cls.user,
            group=cls.group,
        )
        cls.post_image = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с изображением для проверки',
            image=cls.uploaded,
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
        """Проверяем при отправке валидной формы со страницы создания поста
        reverse('posts:post_create') создаётся новая запись в базе данных"""
        count = Post.objects.all().count()
        form_data = {
            'text': 'Test post 2 text. It must be at least 20 symbols.',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertEqual(Post.objects.all().count(), count + 1)

    def test_create_invalid_post(self):
        """Проверяем при отправке не валидной формы со страницы создания поста
        reverse('posts:post_create') не создаётся новая запись в базе данных"""
        count = Post.objects.all().count()
        form_data = {
            'text': 'Test post 2 text',  # less 20 symbols
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertEqual(Post.objects.all().count(), count)

    def test_edit_valid_post(self):
        """Проверяем при отправке валидной формы со страницы редактирования
        поста reverse('posts:post_edit') меняется запись в базе данных"""
        post = PostsFormsTestCase.post
        form_data = {
            'text': 'Test post 2 text. We change this post',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{post.id}'}),
            data=form_data,
        )
        self.assertEqual(Post.objects.get(
            id=post.id).text, 'Test post 2 text. We change this post')
