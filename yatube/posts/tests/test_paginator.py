from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, User
from yatube.settings import POSTS_PER_PAGE


User = get_user_model()


class PaginatorViewsTest(TestCase):
    """Тестирование Paginator"""
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        fake_posts: list = []
        for i in range(13):
            fake_posts.append(Post(
                text=f'Тестовый текст {i}',
                group=self.group,
                author=self.user,
            ))
        Post.objects.bulk_create(fake_posts)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        expected = len(response.context['page_obj'][:POSTS_PER_PAGE])
        self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        expected = len(response.context['page_obj'][:3])
        self.assertEqual(len(response.context['page_obj']), expected)
