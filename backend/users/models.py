from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(
        'Почта',
        max_length=100,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=100,
    )
    first_name = models.CharField(
        'Фамилия',
        max_length=100,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('id',)

    def __str__(self) -> str:
        return self.email
