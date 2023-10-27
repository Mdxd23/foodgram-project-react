from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


STR_MAX_LENGTH = 25
MAX_VALUE = 32767
MIN_VALUE = 1


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200
    )
    measurment_unit = models.CharField(
        'Юнит измерения',
        max_length=200
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return (f'{self.name} - {self.measurment_unit}'[:STR_MAX_LENGTH])


class Tag(models.Model):
    name = models.CharField(
        'Имя',
        max_length=200,
        unique=True
    )
    color = ColorField(
        'Цвет',
        max_length=7,
        unique=True,
        validators=(
            RegexValidator(
                regex='^#?([A-F0-9]{6}|[A-F0-9]{3})$',
                message='Нужно использовать верхний регистер'
            ),
        )
    )
    slug = models.SlugField(
        'Ссылка',
        max_length=200,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


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
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингридиенты',
        related_name='recipes'
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        )
    )
    image = models.ImageField('Изображение рецепта')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)
        unique_together = ('name', 'author')

    def __str__(self):
        return self.name[:STR_MAX_LENGTH]


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
        related_name='recipe_ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=(
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        )
    )

    class Meta:
        verbose_name = 'Ингридиеты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'

    def __str__(self):
        return (
            f'{self.recipe} - {self.ingredient} {self.amount}'[:STR_MAX_LENGTH]
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Любимый рецепт',
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user}, {self.recipe}'[:STR_MAX_LENGTH]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user} Добавил {self.recipe} в корзину'[:STR_MAX_LENGTH]
