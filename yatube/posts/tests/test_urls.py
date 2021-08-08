# posts/tests/tests_url.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group, Post
from django.core.cache import cache


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='title',
            description='description',
            slug='test-slug'
        )
        cls.group2 = Group.objects.create(
            title='title2',
            description='description2',
            slug='test-slug2'
        )
        cls.user1 = User.objects.create_user(username='test-user1')
        cls.user2 = User.objects.create_user(username='test-user2')
        cls.post1 = Post.objects.create(
            text='text1',
            author=PostsURLTests.user1,
            group=PostsURLTests.group,
        )
        cls.post2 = Post.objects.create(
            text='text2',
            author=PostsURLTests.user2,
            group=PostsURLTests.group,
        )
        cls.templates_url_names = {
            'posts/index.html': '/',
            'posts/group.html': f'/group/{cls.group2.slug}/',
            'posts/new_post.html': '/new/',
            'posts/post_edit.html': f'/{cls.user1.username}/1/edit/',
        }
        # 1 - guest, 2 - user1, 2 - user2
        cls.page_access = {
            # а писать enum не затратнее?
            # тут просто статус ведь и все
            '/': (200, 200),
            '/new/': (302, 200),
            f'/group/{cls.group2.slug}/': (200, 200),
            f'/{cls.user1.username}/': (200, 200),
            f'/{cls.user2.username}/': (200, 200),
            f'/{cls.user1.username}/1/': (200, 200),
            f'/{cls.user2.username}/1/': (404, 404),
            f'/{cls.user1.username}/1/edit/': (302, 200),
            f'/{cls.user2.username}/2/edit/': (302, 302),
            'какой-то_бред': (404, 404)
        }
        cls.page_redirect_guest = {
            '/new/': '/auth/login/?next=/new/',
            f'/{cls.user1.username}/1/edit/': ''
            + '/auth/login/?next=/test-user1/1/edit/',
        }
        cls.page_redirect_authorized = {
            f'/{cls.user2.username}/2/edit/': '/'
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user1)

    def test_guest_access_to_page(self):
        """Гость имеет доступ только к определенным страницам"""
        for adress, expected_status in PostsURLTests.page_access.items():
            # для guest ожидается ответ из первого столбца
            expected_status = expected_status[0]
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code,
                                 expected_status)

    def test_authorized_user_access_to_page(self):
        """Юзер имеет доступ только к определенным страницам"""
        for adress, expected_status in PostsURLTests.page_access.items():
            # для user1 ожидается ответ из второго столбца
            expected_status = expected_status[1]
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code,
                                 expected_status)

    def test_redirect_guest(self):
        """Гостя правильно редиректит"""
        for adress, expected_redirect in (
            PostsURLTests.page_redirect_guest.items()
        ):
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(response, expected_redirect)

    def test_redirect_authorized(self):
        """Юзера правильно редиректит"""
        for adress, expected_redirect in (
            PostsURLTests.page_redirect_authorized.items()
        ):
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress, follow=True)
                self.assertRedirects(response, expected_redirect)

    def test_urls_uses_correct_template(self):
        """
        Шаблоны использованы верно
        """
        for template, adress in PostsURLTests.templates_url_names.items():
            with self.subTest(adress=adress):
                cache.clear()
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
