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

    def __str__(self):
        return f'Название:{self.name}, юнит измерения:{self.measurment_unit}'


class Tag(models.Model):
    name = models.CharField('Имя', max_length=200)
    color = models.CharField('Цвет', max_length=7)
    slug = models.SlugField('Ссылка', max_length=200, unique=True)

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
    cooking_time = models.IntegerField('Время приготовления')
    image = models.ImageField(
        'Изображение рецепта',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


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
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=0
    )

    class Meta:
        verbose_name = 'Ингридиеты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'


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

    def __str__(self):
        return f'{self.user}, {self.recipe}'


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

    def __str__(self):
        return f'{self.user} Добавил {self.recipe} в корзину'
