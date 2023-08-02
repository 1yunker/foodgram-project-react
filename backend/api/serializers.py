import base64

# from django.conf import settings
# from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

# from djoser.conf import settings
from djoser.serializers import UserCreateSerializer

from rest_framework import serializers
from rest_framework.decorators import action
# from rest_framework.fields import CurrentUserDefault
# from rest_framework.validators import UniqueTogetherValidator

from api.permissions import IsOwner
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(
        read_only=True, slug_field='name')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class SpecialUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    # def get_is_subscribed(self, obj):
    #     return obj.following.filter(
    #         user=self.context['request'].user.id).exists()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.following.filter(user=user).exists()
        )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password',)


class RecipeCreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit.name'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = SpecialUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        return obj.in_favorites.filter(
            user=self.context['request'].user.id).exists()

    def get_is_in_shopping_cart(self, obj):
        return obj.in_shopping_cart.filter(
            user=self.context['request'].user.id).exists()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeCreateIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(
                recipe=recipe,
                tag=tag
            )
        for ingredient in ingredients:
            ingredient_id = ingredient.get('ingredient')
            current_ingredient = Ingredient.objects.get(pk=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient.get('amount')
            )
        return recipe

    @action(permission_classes=(IsOwner,), detail=False,)
    def update(self, instance, validated_data):
        # Удаляем данные из подчиненных таблиц
        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        tags = validated_data.pop('tags')
        for tag in tags:
            RecipeTag.objects.create(
                recipe=instance,
                tag=tag
            )
        ingredients = validated_data.pop('ingredients')
        for ingredient in ingredients:
            ingredient_id = ingredient.get('ingredient')
            current_ingredient = Ingredient.objects.get(pk=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=current_ingredient,
                amount=ingredient.get('amount')
            )

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
    """ Сериализатор для отображения избранного. """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(SpecialUserSerializer):
    """ Сериализатор для отображения подписок пользователя. """

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

    class Meta(SpecialUserSerializer.Meta):
        fields = SpecialUserSerializer.Meta.fields + (
            'recipes', 'recipes_count',)
