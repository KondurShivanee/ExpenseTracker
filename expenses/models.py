from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Category model for organizing expenses."""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='bi-tag')  # Bootstrap icon class
    color = models.CharField(max_length=7, default='#6c757d')  # Hex color

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    """Expense model for tracking individual expenses."""
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expenses'
    )
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description} - ${self.amount}"

    def get_absolute_url(self):
        return reverse('expense_list')
