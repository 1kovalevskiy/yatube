import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from time import sleep

from posts.models import Group, Post

User = get_user_model()


class PostPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.group1 = Group.objects.create(
            title='title',
            description='description',
            slug='test-group1'
        )
        cls.group2 = Group.objects.create(
            title='title2',
            description='description2',
            slug='test-group2'
        )
        cls.group3 = Group.objects.create(
            title='title3',
            description='description3',
            slug='test-group3'
        )
        cls.user = User.objects.create_user(username='TestUser')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        # Не уверен, что через bulk_create у них будет разная дата создания
        for i in range(13):
            Post.objects.create(
                text=f'text{i}',
                author=PostPageTests.user,
                group=PostPageTests.group1,
                image=cls.uploaded
            )
            # пришлось ввести задержку, чтобы посты создавались в разное время
            # а то последним иногда был и 11, и 10 пост, вместо 12!
            sleep(0.005)
        cls.templates_page_names = {
            'posts/index.html': reverse('index'),
            'posts/new_post.html': reverse('new_post'),
            'posts/group.html': reverse('group_posts',
                                        args=[PostPageTests.group1.slug]),
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        cls.page_with_post_list = [
            reverse('index'),
            reverse('group_posts', args=[PostPageTests.group1.slug]),
            reverse('profile', args=[PostPageTests.user.username]),
        ]
    
    @classmethod
    def tearDownClass(cls):
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок|файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPageTests.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in (
            PostPageTests.templates_page_names.items()
        ):
            with self.subTest(template=template):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_first_page_contains_ten_records(self):
        """Пагинатор передал 10 постов на первую страницу и 3 на вторую"""
        for url in PostPageTests.page_with_post_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context['page']), 10)
                response2 = self.guest_client.get(url + '?page=2')
                self.assertEqual(len(response2.context['page']), 3)

    def test_page_with_list_show_correct_context(self):
        """
        Шаблоны страниц со списками постов сформированы\
        с правильным контекстом.
        """
        for url in PostPageTests.page_with_post_list:
            with self.subTest(url=url):
                cache.clear()
                response = self.authorized_client.get(url)
                # Взяли первый элемент из списка и проверили, что его
                # содержание совпадает с ожидаемым
                pk = Post.objects.filter(text='text12').get().pk

                post = response.context['page'][0]
                post_text_0 = post.text
                post_author_0 = post.author
                post_group_0 = post.group
                post_image_0 = post.image
                self.assertEqual(post_text_0, 'text12')
                self.assertEqual(post_author_0, PostPageTests.user)
                self.assertEqual(post_group_0, PostPageTests.group1)
                self.assertEqual(post_image_0, 
                    Post.objects.get(id=pk).image
                )

    def test_page_with_form_show_correct_context(self):
        """Шаблоны с формами сформированы с правильным контекстом."""
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        page_with_form = ['/new/', '/TestUser/12/edit/']
        for url in page_with_form:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in PostPageTests.form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_page_with_post_show_correct_context(self):
        """
        Шаблон поста сформированы с правильным контекстом.
        """
        pk = Post.objects.filter(text='text12').get().pk
        response = self.authorized_client.get(f'/TestUser/{pk}/')
        # Взяли первый элемент из списка и проверили, что его
        # содержание совпадает с ожидаемым
        post = response.context['post']
        post_text_0 = post.text
        post_author_0 = post.author
        post_group_0 = post.group
        post_image_0 = post.image
        self.assertEqual(post_text_0, 'text12')
        self.assertEqual(post_author_0, PostPageTests.user)
        self.assertEqual(post_group_0, PostPageTests.group1)
        self.assertEqual(post_image_0, 
            Post.objects.get(id=pk).image
        )

    def test_create_new_post_and_show_in_group1(self):
        """Запись создалась и отображается в группе 1"""
        Post.objects.create(
            text='new-post',
            author=PostPageTests.user,
            group=PostPageTests.group1,
        )
        for url in PostPageTests.page_with_post_list:
            with self.subTest(url=url):
                cache.clear()
                response = self.authorized_client.get(url)
                post = response.context['page'][0]
                self.assertEqual(post.text, 'new-post')

    def test_group2_is_empty(self):
        """Запись не отображается в группе 2"""
        self.group4 = Group.objects.create(
            title='title4',
            description='description4',
            slug='test-group4'
        )
        Post.objects.create(
            text='new-post',
            author=PostPageTests.user,
            group=PostPageTests.group1,
        )
        response = self.authorized_client.get(
            reverse('group_posts', args=[self.group4.slug]))
        objects = response.context['page']
        # Не знал, что надо objects.paginator.count
        # Пытался objects.count - не работало
        self.assertEqual(objects.paginator.count, 0)

    def test_index_cache(self):
        post_count = Post.objects.all().count()
        Post.objects.create(
            text='new-post-with-cache',
            author=PostPageTests.user,
            group=PostPageTests.group1,
        )
        response = self.authorized_client.get('/')
        page = response.content.decode()
        self.assertNotIn('new-post-with-cache', page)
        cache.clear()
        response = self.authorized_client.get('/')
        page = response.content.decode()
        self.assertIn('new-post-with-cache', page)