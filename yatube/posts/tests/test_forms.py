from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Name',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовое название группы 2',
            slug='test-slug2',
            description='Тестовое описание группы 2'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_create_post(self):
        """Проверка создания записи пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': 'Name'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group_id, form_data['group'])

    def test_user_edit_post(self):
        """Проверка редактирования записи пользователем."""
        self.post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
            group=self.group,
        )
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertTrue(post.text == form_data['text'])
        self.assertTrue(post.author == self.user)
        self.assertTrue(post.group_id == form_data['group'])
        self.assertTrue(Post.objects.filter(id=self.post.id,
                                            group=self.group_2.id,
                                            author=self.user,
                                            ).exists())
