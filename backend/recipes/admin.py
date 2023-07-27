from django.contrib import admin

from recipes.models import Ingredient, Favorite, Recipe, ShoppingCart, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_editable = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)
    list_per_page = 10
    list_select_related = True
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'text', 'image',
                    'cooking_time', 'pub_date',)
    search_fields = ('author', 'name',)
    list_filter = ('author', 'name', 'tags', 'cooking_time',)
    list_select_related = True
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    list_editable = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
