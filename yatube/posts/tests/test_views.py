from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='Тестовое заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def post_ifo_massage(self, context):
        with self.subTest(context=context):
            self.assertEqual(context.text, self.post.text)
            self.assertEqual(context.pub_date, self.post.pub_date)
            self.assertEqual(context.author, self.post.author)
            self.assertEqual(context.group.id, self.post.group.id)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse(
                'posts:home'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'Name'}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): 'posts/post_create.html',
            reverse(
                'posts:create'): 'posts/post_create.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон home.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:home'))
        self.post_ifo_massage(response.context['page_obj'][0])

    def test_group_page_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)
        self.post_ifo_massage(response.context['page_obj'][0])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'Name'}))
        self.assertEqual(response.context['author'], self.user)
        self.post_ifo_massage(response.context['page_obj'][0])

    def test_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        self.post_ifo_massage(response.context['post'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Name',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.test_posts = []
        for i in range(13):
            cls.test_posts.append(Post(
                text=f'Тестовый пост №{i}',
                group=cls.group,
                author=cls.user))
        Post.objects.bulk_create(cls.test_posts)

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""
        posts_on_first_page = 10
        posts_on_second_page = 3
        url_pages = [
            reverse('posts:home'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': 'Name'}),
        ]
        for rev in url_pages:
            with self.subTest(rev=rev):
                self.assertEqual(len(self.unauthorized_client.get(
                    rev).context.get('page_obj')),
                    posts_on_first_page
                )
                self.assertEqual(len(self.unauthorized_client.get(
                    rev + '?page=2').context.get('page_obj')),
                    posts_on_second_page
                )
