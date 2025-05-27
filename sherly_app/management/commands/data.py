# Assuming this code is added in management/commands/add_products.py

import random
import string
from django.core.management.base import BaseCommand
from sherly_app.models import Produit, Famille

class Command(BaseCommand):
    help = 'Add products'

    def handle(self, *args, **options):
        self.add_products()

    @staticmethod
    def add_products():
        # Retrieve the Famille instance with the desired name
        famille_name = "MENICON"
        famille, _ = Famille.objects.get_or_create(famille=famille_name)

        products_data = [
            ("MENICON MIRU 1 DAY", 30, 15.42),
            ("MENICON MIRU 1 DAY TORIC", 30, 19.74),
            ("MENICON MIRU 1 DAY UPSIDE", 30, 16.55),
            ("MENICON MIRU 1 DAY UPSIDE MULTIFOCAL", 30, 26.23),
            ("MENICON MIRU 1 MONTH", 6, 20.21),
            ("MENICON MIRU 1 MONTH FOR ASTIGMATISM", 6, 27.74),
            ("MENICON MIRU 1 MONTH MULTIFOCAL", 6, 40.33),
            ("MENICON PREMIO 2 WEEKS", 6, 18.71),
            ("MENICON PREMIO TORIC", 6, 22.47),
        ]

        for name, conditionnement_count, prix in products_data:
            produit = Produit.objects.create(
                designation=name,
                famille=famille,
                conditionnement_count=conditionnement_count,
                prix=prix,
            )
            print(f"Product added: {produit}")

        print("Products added successfully.")
