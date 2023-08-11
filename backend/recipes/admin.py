from django.contrib import admin

from recipes.models import (Ingredient, Favorite, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_editable = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)
    list_per_page = 10
    list_select_related = True
    empty_value_display = '-пусто-'


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    verbose_name = 'Тег'
    verbose_name_plural = 'Теги'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fk_name = 'recipe'
    extra = 1
    verbose_name = 'Ингридиент'
    verbose_name_plural = 'Ингридиенты'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'text', 'image',
                    'cooking_time', 'pub_date',)
    inlines = (TagInline, RecipeIngredientInline,)
    readonly_fields = ('count_in_favorites',)

    search_fields = ('author', 'name',)
    list_filter = ('author', 'name', 'tags', 'cooking_time',)
    list_select_related = True
    empty_value_display = '-пусто-'

    @admin.display(
        description='Общее число добавлений в избранное'
    )
    def count_in_favorites(self, obj):
        return obj.in_favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    list_editable = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
