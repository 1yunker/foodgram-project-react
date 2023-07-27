import base64

# from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag

User = get_user_model()


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)
        model = User


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    # ingredients = RecipeIngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredient_id = ingredient.get('ingredient')
            current_ingredient = Ingredient.objects.get(pk=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient.get('amount')
            )
        for tag in tags:
            RecipeTag.objects.create(
                recipe=recipe,
                tag=tag
            )
        return recipe

    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.color = validated_data.get('color', instance.color)
    #     instance.birth_year = validated_data.get(
    #         'birth_year', instance.birth_year
    #     )
    #     instance.image = validated_data.get('image', instance.image)

    #     if 'achievements' not in validated_data:
    #         instance.save()
    #         return instance

    #     achievements_data = validated_data.pop('achievements')
    #     lst = []
    #     for achievement in achievements_data:
    #         current_achievement, status = Achievement.objects.get_or_create(
    #             **achievement
    #         )
    #         lst.append(current_achievement)
    #     instance.achievements.set(lst)

    #     instance.save()
    #     return instance

    class Meta:
        fields = ('name', 'text', 'image', 'cooking_time',
                  'ingredients', 'tags')
        model = Recipe
