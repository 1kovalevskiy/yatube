import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.forms import PostForm
from posts.models import Group, Post
import os


User = get_user_model()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

TESTMEDIA = os.path.join(BASE_DIR, "testmedia")


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # settings.MEDIA_ROOT = TESTMEDIA

        cls.group = Group.objects.create(
            title='title',
            description='description',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='TestUser')
        Post.objects.create(
            text='text',
            author=PostFormTests.user,
            group=PostFormTests.group,
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок|файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TESTMEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    @override_settings(MEDIA_ROOT=TESTMEDIA)
    def test_create_new_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'author': PostFormTests.user,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                author=PostFormTests.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        Post.objects.create(
            text='Тест редактирования',
            author=PostFormTests.user,
            group=PostFormTests.group,
        )
        posts_count = Post.objects.count()
        pk = Post.objects.filter(text='Тест редактирования').get().pk
        form_data = {
            'text': 'Успешно отредактировано',
            'author': PostFormTests.user,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': PostFormTests.user.username,
                'post_id': pk
            }),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post', kwargs={
                             'username': PostFormTests.user.username,
                             'post_id': pk
                             }))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Успешно отредактировано',
                author=PostFormTests.user,
            ).exists()
        )

    def test_guest_create_new_post(self):
        """Гость не может создать запись в Post."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст от гостя',
            'author': PostFormTests.user,
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, '/auth/login/?next=/new/')
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count)

    def test_authorized_can_comment(self):
        """Доступ к комментам есть только у авторизированного"""
        pk = Post.objects.get(text='text').pk
        form_data = {
            'text': 'comment',
        }
        response = self.authorized_client.post(
            reverse('add_comment',
                    kwargs={'username': PostFormTests.user.username,
                            'post_id': pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post', kwargs={
                             'username': PostFormTests.user.username,
                             'post_id': pk
                             }))
        comment_count = PostFormTests.user.comments.count()
        self.assertEqual(comment_count, 1)

    def test_guest_can_comment(self):
        """Гость не имеет доступа к комментам"""
        pk = Post.objects.get(text='text').pk
        form_data = {
            'text': 'comment',
        }
        response = self.guest_client.post(
            reverse('add_comment',
                    kwargs={'username': PostFormTests.user.username,
                            'post_id': pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/TestUser/1/comment')
        comment_count = PostFormTests.user.comments.count()
        self.assertEqual(comment_count, 0)
