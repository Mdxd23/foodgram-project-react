from django.contrib.auth.models import AbstractUser
from django.db import models

STR_MAX_LENGTH = 25


class User(AbstractUser):
    email = models.EmailField(
        'Почта',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    password = models.CharField(
        'Пароль',
        max_length=150
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        return self.email[:STR_MAX_LENGTH]


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='subscription',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber',
    )

    class Meta:
        unique_together = ('author', 'subscriber')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'{self.subscriber.username} пописан на {self.author.username}'
                )[:STR_MAX_LENGTH]
