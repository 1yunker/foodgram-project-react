from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from colorfield.fields import ColorField


class Tag(models.Model):
    """Тег."""

    name = models.CharField(
        'Название',
        max_length=settings.MAX_LENGTH_NAME,
        unique=True
    )
    color = ColorField(
        'Цвет в HEX',
        max_length=7,
        unique=True,
        validators=(
            RegexValidator(
                regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                message=('Введите цвет в HEX-формате: например, #E26C2D')
            ),
        )
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=settings.MAX_LENGTH_SLUG,
        unique=True,
        validators=(
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message=('Введите слаг в формате [-a-zA-Z0-9_]')
            ),
        )
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Measurement(models.Model):
    """Единица измерения."""

    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент."""

    name = models.CharField(
        'Название',
        max_length=settings.MAX_LENGTH_NAME
    )
    measurement_unit = models.ForeignKey(
        Measurement,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название',
        max_length=settings.MAX_LENGTH_NAME,
        unique=True
    )
    text = models.TextField('Описание')
    image = models.ImageField('Ссылка на картинку')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (мин.)',
        default=1,
        validators=(MinValueValidator(1),)
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Список ингредиентов'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Список тегов'
    )
    who_likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Favorite',
        related_name='favorite_recipes',
        verbose_name='Список избранного'
    )
    who_buys = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ShoppingCart',
        related_name='recipes_in_shopping_cart',
        verbose_name='Список покупок'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Ингредиенты в рецепте."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        # related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        default=1,
        validators=(MinValueValidator(1),)
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredients',
            ),
        )

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'


class RecipeTag(models.Model):
    """Теги в рецепте."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tags',
            ),
        )

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class Favorite(models.Model):
    """Избранные рецепты пользователей."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_vaforites'
            ),
        )

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    """Список покупок пользователей."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Список покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_items'
            ),
        )

    def __str__(self):
        return f'{self.user} {self.recipe}'
