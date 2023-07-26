from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Tag(models.Model):
    """Тег"""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        unique=True)
    slug = models.SlugField(
        max_length=settings.MAX_LENGTH_SLUG,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Measurement(models.Model):
    """Единица измерения"""

    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент"""

    name = models.CharField(max_length=settings.MAX_LENGTH_NAME)
    measurement_unit = models.ForeignKey(
        Measurement,
        null=True,
        on_delete=models.SET_NULL,
        related_name='ingredients'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт"""

    author = models.ForeignKey(
        # User,
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True
    )
    text = models.TextField()
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), ])

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredients',
            ),
        )

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
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


class Subscrption(models.Model):
    """Подписка на авторов рецептов"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_following'
            )
        ]


class Favorite(models.Model):
    """Избранные рецепты"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_vaforites'
            )
        ]


class ShoppingCart(models.Model):
    """Список покупок"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_items'
            )
        ]
