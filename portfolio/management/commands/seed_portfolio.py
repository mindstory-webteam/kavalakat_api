"""
Seeds default portfolio data matching the Kavalakat website design.
Usage:  py manage.py seed_portfolio
        py manage.py seed_portfolio --clear   (wipe & re-seed)
"""
from django.core.management.base import BaseCommand
from portfolio.models import Category, Item


SEED = {
    'Trading': {
        'order': 1,
        'items': [
            'CEMENT',
            'STEELS',
            'ROOFING SOLUTIONS',
            'WHITE CEMENT PAINT',
            'CONSTRUCTION CHEMICALS',
        ],
    },
    'Distribution': {
        'order': 2,
        'items': [
            'ULTRATECH',
            'JK CEMENT',
            'TATA STEEL',
            'JSW STEEL',
            'ASIAN PAINTS',
        ],
    },
    'Services': {
        'order': 3,
        'items': [
            'KAVALAKAT GROUP',
            'ALITE ENCLAVES',
            'NEEY VEDHYAM',
        ],
    },
}


class Command(BaseCommand):
    help = 'Seed default portfolio categories and items for Kavalakat'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete all existing portfolio data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Item.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all portfolio data.'))

        cats_created  = 0
        items_created = 0

        for cat_name, data in SEED.items():
            cat, new = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    'slug':      cat_name.lower(),
                    'order':     data['order'],
                    'is_active': True,
                }
            )
            if new:
                cats_created += 1
                self.stdout.write(f'  + Category: {cat_name}')

            for idx, item_name in enumerate(data['items'], start=1):
                item, new_item = Item.objects.get_or_create(
                    name=item_name,
                    category=cat,
                    defaults={'order': idx, 'is_active': True}
                )
                if new_item:
                    items_created += 1
                    self.stdout.write(f'      + Item: {item_name}')

        self.stdout.write('')
        if cats_created or items_created:
            self.stdout.write(self.style.SUCCESS(
                f'Done! Created {cats_created} categories and {items_created} items.'
            ))
        else:
            self.stdout.write(
                'All data already exists. Use --clear to reset and re-seed.'
            )
