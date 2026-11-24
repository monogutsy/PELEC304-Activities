import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Product


class Command(BaseCommand):
    help = "Add the original 20 sample products without changing existing records."

    @transaction.atomic
    def handle(self, *args, **options):
        fixture = Path(__file__).resolve().parents[2] / "fixtures" / "products.json"
        records = json.loads(fixture.read_text(encoding="utf-8"))
        created_count = 0
        for record in records:
            product, created = Product.objects.get_or_create(
                pk=record["pk"], defaults=record["fields"]
            )
            created_count += created
        self.stdout.write(self.style.SUCCESS(
            f"Added {created_count} products; existing records preserved."
        ))
