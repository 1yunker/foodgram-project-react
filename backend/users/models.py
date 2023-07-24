from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


from users.validators import username_validator


class User(AbstractUser):
    username = models.CharField(
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True,
        validators=(UnicodeUsernameValidator(), username_validator,),
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        blank=False,
    )

    class Meta:
        ordering = ('username',)

    @property
    def is_admin(self):
        return (self.is_superuser or self.is_staff)

    def __str__(self):
        return self.username
