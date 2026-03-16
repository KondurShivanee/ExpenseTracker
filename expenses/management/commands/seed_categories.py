from django.core.management.base import BaseCommand
from expenses.models import Category


class Command(BaseCommand):
    help = 'Seed the database with default expense categories'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Food & Dining', 'icon': 'bi-cup-hot', 'color': '#fd7e14'},
            {'name': 'Transportation', 'icon': 'bi-car-front', 'color': '#0dcaf0'},
            {'name': 'Shopping', 'icon': 'bi-cart', 'color': '#d63384'},
            {'name': 'Entertainment', 'icon': 'bi-film', 'color': '#6f42c1'},
            {'name': 'Bills & Utilities', 'icon': 'bi-lightning', 'color': '#ffc107'},
            {'name': 'Healthcare', 'icon': 'bi-heart-pulse', 'color': '#dc3545'},
            {'name': 'Education', 'icon': 'bi-book', 'color': '#198754'},
            {'name': 'Travel', 'icon': 'bi-airplane', 'color': '#0d6efd'},
            {'name': 'Groceries', 'icon': 'bi-basket', 'color': '#20c997'},
            {'name': 'Other', 'icon': 'bi-three-dots', 'color': '#6c757d'},
        ]

        created_count = 0
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created category: {category.name}")
            else:
                self.stdout.write(f"Category already exists: {category.name}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {created_count} new categories')
        )
