from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Clears all data except superusers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force the operation without confirmation',
        )

    def handle(self, *args, **options):
        if not options['force']:
            confirm = input(
                'This will delete ALL data except superusers. Are you sure? [y/N]: '
            )
            if confirm.lower() != 'y':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return

        try:
            with transaction.atomic():
                # Delete all non-admin users
                non_admins = User.objects.filter(is_admin=False)
                non_admin_count = non_admins.count()
                non_admins.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted {non_admin_count} non-admin users')
                )

                # Delete all products
                products = Product.objects.all()
                product_count = products.count()
                products.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted {product_count} products')
                )

                self.stdout.write(self.style.SUCCESS('Successfully cleared all data except admin users'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'An error occurred: {str(e)}')
            ) 