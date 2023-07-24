from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Тег"""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True
    )
    color = models.CharField(max_length=7)
    slug = models.SlugField(
        max_length=settings.MAX_LENGTH_SLUG,
        unique=True
    )

    class Meta:
        ordering = ('name',)


class Measurement(models.Model):
    """Единица измерения"""

    name = models.CharField(max_length=10, unique=True)


class Ingredient(models.Model):
    """Ингредиент"""

    name = models.CharField(max_length=settings.MAX_LENGTH_NAME)
    measurement_unit = models.ForeignKey(
        Measurement,
        on_delete=models.SET_NULL,
        related_name='ingredients'
    )

    class Meta:
        ordering = ('name',)


class Recipe(models.Model):
    """Рецепт"""

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
        validators=MinValueValidator(1)
    )
    author = models.ForeignKey(
        User,
        # settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )
    tag = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=MinValueValidator(1))

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
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
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
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_recipes'
            )
        ]


class ShoppingCart(models.Model):
    """Список покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_recipes'
            )
        ]
