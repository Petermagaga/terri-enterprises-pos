from django.core.exceptions import ValidationError
from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=150)

    contact_person = models.CharField(
        max_length=150,
        blank=True,
    )

    phone = models.CharField(max_length=30)

    email = models.EmailField(
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def clean(self):
        super().clean()

        if not self.name or not self.name.strip():
            raise ValidationError({
                "name": "Supplier name cannot be empty."
            })

        if not self.phone or not self.phone.strip():
            raise ValidationError({
                "phone": "Supplier phone number cannot be empty."
            })

        self.name = self.name.strip()
        self.phone = self.phone.strip()

    def __str__(self):
        return self.name