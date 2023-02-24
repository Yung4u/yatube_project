from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
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
            content_type='image/gif',
        )
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый пост',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertContains(response, "<img")

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
