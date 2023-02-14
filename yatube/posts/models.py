from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="название группы")
    slug = models.SlugField(unique=True, verbose_name="ссылка группы")
    description = models.TextField(verbose_name="текст группы")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="текст поста")
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name="дата поста")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='post'
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('-pub_date',)
