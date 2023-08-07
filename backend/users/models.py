from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


from users.validators import username_validator


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Пользователь',
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True,
        validators=(UnicodeUsernameValidator(), username_validator,)
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        blank=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        return (self.is_superuser or self.is_staff)

    def __str__(self):
        return self.username


class Subscrption(models.Model):
    """Подписка на авторов рецептов."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
