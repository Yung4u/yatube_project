from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Post, Group, Comment, Follow, User


User = get_user_model()


class PostViewsTests(TestCase):
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

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_1 = User.objects.create_user(username='Following')
        self.user_following = Client()
        self.user_following.force_login(self.user_1)
        self.user_2 = User.objects.create_user(username='Follower')
        self.client_auth_follower = Client()
        self.client_auth_follower.force_login(self.user_2)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        form_fields = {
            first_object.author.username: 'auth',
            first_object.text: 'Тестовый пост',
            first_object.group.title: 'Тестовая группа',
        }

        for value, expected in form_fields.items():
            self.assertEqual(value, expected)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug}
        ))
        form_fields = {
            'title': self.group.title,
            'description': self.group.description,
            'slug': self.group.slug,
            'id': self.group.id,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertEqual(
                    getattr(response.context.get('group'), value), expected
                )

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        ))
        self.assertEqual(response.context['post'], self.post)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # def test_post_edit_show_correct_context(self):
    #     """Шаблон post_edit сформирован с правильным контекстом."""
    #     response = self.authorized_client.get(reverse(
    #         'posts:post_edit', kwargs={'post_id': self.post.id}
    #     ))
    #     form_fields = {
    #         'text': forms.fields.CharField,
    #         'group': forms.fields.ChoiceField,
    #     }
    #     for value, expected in form_fields.items():
    #         with self.subTest(value=value):
    #             form_field = response.context.get('form').fields.get(value)
    #             self.assertIsInstance(form_field, expected)

    def test_auth_user_may_post_comment(self):
        """Комментировать посты может только авторизированный пользователь"""
        first_comment_count = Comment.objects.count()
        form_data = {'text': 'Тестовый комментарий'}
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            first_comment_count + 1,
            Comment.objects.count()
        )

    def test_subscription_feed(self):
        """Появление записи в ленте подписчиков"""
        author = User.objects.create_user(username='auth_following')
        following_text = 'Тестовый пост'
        Follow.objects.create(user=self.user, author=author)
        Post.objects.create(
            author=author,
            text=following_text,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, following_text)
        Follow.objects.filter(user=self.user, author=author).delete()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_follow_auth_can_follow_delete(self):
        """Создание и удаления подписчика"""
        follow = Follow.objects.create(
            user=self.user,
            author=self.user_1,
        )
        result = self.user_1.following.count()
        self.assertEqual(result, 1)
        follow = Follow.objects.get(author=self.user_1)
        follow.delete()
        result =self.user_1.following.count()
        self.assertEqual(result, 0)

    def text_cache_index(self):
        """Проверка работы кэша"""
        response = Post.guest_client.get(reverse('posts:index'))
        self.assertContains(response, Post.post.text)
        response = Post.guest_client.get(reverse('posts:index'))
        self.assertContains(response, Post.post.text)
        Post.objects.get(pk=Post.post.id).delete()
        response = Post.guest_client.get(reverse('posts:index'))
        self.assertContains(response, Post.post.text)
        response = Post.guest_client.get(reverse('posts:index'))
        self.assertNotContains(response, Post.post.text)

    def test_unfollow(self):
        """Тест на возможность отписки"""
        self.client_auth_follower.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_following}
        ))
        self.client_auth_follower.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_following}
        ))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_follow_numbers(self):
        """Отображение постов по подписке"""
        follow = Follow.objects.create(
            user=self.user,
            author=self.user_1,
        )
        response_1 = self.authorized_client.get(f'profile/{self.user_1.username}/follow/')
        response_2 = self.authorized_client.get(f'profile/{self.user_1.username}/follow/')
        result = self.user.follower.count()
        self.assertEqual(result, 1)