from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


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


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=200)
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='recipes',
        through='TagInRecipe'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe'
    )
    text = models.TextField('Описание')
    cooking_time = models.IntegerField('Время приготовления')
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='static/'
    )


class TagInRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_used'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_used'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=0
    )
