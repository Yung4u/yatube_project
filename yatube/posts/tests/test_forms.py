from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, Group, User
from http import HTTPStatus


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.form = PostForm()
        cls.posts_count = Post.objects.count()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает запись в Post"""
        form_data = {
            'id': self.group.id,
            'text': 'Тестовый пост',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertTrue(Post.objects.filter(
            id=self.group.id,
            group=PostCreateFormTests.group,
        ).exists())

    def test_post_edit(self):
        """Валидная форма редактирует запись (текст и группу) в Post"""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        self.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-group',
            description='Тестовое описание',
        )
        form_data = {
            'text': 'Текст в форме',
            'group': self.group2.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name1 = 'Данные поста не совпадают'
        self.assertTrue(Post.objects.filter(
                        group=self.group2.id,
                        author=self.user,
                        pub_date=self.post.pub_date
                        ).exists(), error_name1)
        error_name1 = 'Пользователь не может изменить содержание поста'
        self.assertNotEqual(self.post.text, form_data['text'], error_name1)
        error_name2 = 'Пользователь не может изменить группу поста'
        self.assertNotEqual(self.post.group, form_data['group'], error_name2)
