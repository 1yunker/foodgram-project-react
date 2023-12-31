from django.db import transaction
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerialiser,
    UserSerializer as DjoserUserSerialiser)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор отображения ингредиента."""

    measurement_unit = serializers.SlugRelatedField(
        read_only=True, slug_field='name')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор отображения тега."""

    class Meta:
        model = Tag
        fields = '__all__'


class UserSerializer(DjoserUserSerialiser):
    """Сериализатор пользователя при отображении пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        return obj.following.filter(
            user=self.context['request'].user.id).exists()

    class Meta(DjoserUserSerialiser.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',)


class UserCreateSerializer(DjoserUserCreateSerialiser):
    """Сериализатор пользователя при создании пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password',)


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов при создании рецепта."""

    id = serializers.IntegerField(source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов при отображении рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit.name'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецепта."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        exclude = ('pub_date', 'who_likes', 'who_buys',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    def create_tags(self, tags, recipe):
        data = []
        for tag in tags:
            data.append(RecipeTag(recipe=recipe, tag=tag))
        RecipeTag.objects.bulk_create(data)

    def find_idx(self, lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1

    def create_ingredients(self, ingredients, recipe):
        data = []
        obj_ingredients = Ingredient.objects.filter(
            pk__in=[ingredient['ingredient'] for ingredient in ingredients]
        )
        for obj_ingredient in obj_ingredients:
            idx = self.find_idx(ingredients, 'ingredient', obj_ingredient.pk)
            data.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=obj_ingredient,
                    amount=ingredients[idx].get('amount')
                )
            )
        RecipeIngredient.objects.bulk_create(data)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        tags = validated_data.pop('tags')
        RecipeTag.objects.filter(recipe=instance).delete()
        self.create_tags(tags, instance)

        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients, instance)

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    class Meta:
        fields = ('name', 'text', 'image', 'cooking_time',
                  'ingredients', 'tags')
        model = Recipe


class FavoriteGetSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения избранного."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для отображения подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return FavoriteGetSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
