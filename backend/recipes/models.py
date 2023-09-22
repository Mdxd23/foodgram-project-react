from django.db import models


# Create your models here.
class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurment_unit = models.CharField('Юнит измерения', max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name = 'Ингредиенты'
