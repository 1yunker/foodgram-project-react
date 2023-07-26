from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_staff',
                    'is_active', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
