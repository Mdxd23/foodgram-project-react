# Generated by Django 4.2.5 on 2023-09-29 03:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_remove_ingredientinrecipe_ingredient_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientinrecipe',
            options={'verbose_name': 'Ингридиеты в рецепте', 'verbose_name_plural': 'Ингридиенты в рецепте'},
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient', to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]
