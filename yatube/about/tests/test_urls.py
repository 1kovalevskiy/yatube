from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus


class StaticViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.static_page = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html'
        }

    def setUp(self):
        self.guest_client = Client()

    def test_author_page_accessible_by_name(self):
        """URL, генерируемый при запросе about, доступен."""
        for name in StaticViewsTests.static_page.keys():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)
