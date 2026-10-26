from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    date= models.DateTimeField(default=timezone.localdate)

    class Meta:
        ordering = ['-date', 'id']

    def __str__(self):
        return f"{self.amount} {self.category} {self.description}"

