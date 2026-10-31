from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    """
    Ensures that users created through createsuperuser
    automatically receive the OWNER role.
    """

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", self.model.Role.OWNER)

        return super().create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields,
        )


class User(AbstractUser):

    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        CASHIER = "CASHIER", "Cashier"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CASHIER,
        db_index=True,
    )

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"