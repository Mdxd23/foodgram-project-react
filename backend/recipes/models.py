from django.db import models


# Create your models here.
class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurment_unit = models.CharField('Юнит измерения', max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    name = models.CharField('Имя', max_length=200)
    color = models.CharField('Цвет', max_length=7)
    slug = models.SlugField('Ссылка', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
