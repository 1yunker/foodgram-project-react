from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 6)
