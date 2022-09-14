from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Group',
        help_text='Группа к которой относится пост'
    )

    class Meta:
        verbose_name = 'Post'
        ordering = ['-pub_date']

    def __str__(self):
        # выводим текст поста
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='text-slug'
    )
    description = models.TextField(
        max_length=500,
        verbose_name='Описание'
    )

    def __str__(self):
        return self.title[:50]

    class Meta:
        verbose_name = 'Group'
