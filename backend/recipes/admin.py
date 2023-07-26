from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)
    list_editable = ('name', 'measurement_unit',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author',)
    search_fields = ('pk', 'author', 'name',)
    list_filter = ('author', 'tags', 'cooking_time', 'pub_date',)
    list_editable = ('author', 'name', 'text', 'cooking_time',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    list_editable = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
