from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import User, Subscrption


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_staff',
                    'is_active', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Subscrption)
