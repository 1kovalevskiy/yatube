from django.test import TestCase
from posts.models import Group, Post
from django.contrib.auth import get_user_model

User = get_user_model()


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            username='testuser',
            first_name='testuser',
            last_name='testuser',
            email='test@mail.ru'
        )

        cls.group = Group.objects.create(
            title='f' * 300,
            slug='testgroup',
            description='testgroup',
        )

        cls.post = Post.objects.create(
            text='f' * 300,
            author=cls.user,
            group=cls.group,
        )
        cls.objects = {
            PostsModelTest.group: PostsModelTest.group.title,
            PostsModelTest.post: PostsModelTest.post.text[:15]
        }

    def test_str(self):
        for model_object, expected_name in PostsModelTest.objects.items():
            with self.subTest(model_object=model_object):
                self.assertEqual(expected_name, str(model_object))
