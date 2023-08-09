from django.db.models import F, Sum

from recipes.models import RecipeIngredient


def generate_shopping_list(user):
    """Формирование списка покупок в текстовом виде."""

    # Берем список рецептов пользователя из корзины
    recipes = user.in_shopping_cart.values('recipe')
    ingredients = RecipeIngredient.objects.filter(
        recipe__in=recipes
    ).values(
        name=F('ingredient__name'),
        m_unit=F('ingredient__measurement_unit__name')
    ).annotate(
        amount=Sum('amount')
    ).order_by('name')

    shopping_list = ('Список покупок:\n\n')
    shopping_list += '\n'.join([
        f'{ingredient["name"]} ({ingredient["m_unit"]}) - '
        f'{ingredient["amount"]}'
        for ingredient in ingredients
    ])
    return shopping_list
