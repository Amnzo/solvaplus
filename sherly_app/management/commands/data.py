from django.core.management.base import BaseCommand
from django.db import transaction
from sherly_app.models import Famille, Produit
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Populate Famille and Produit models with sample data'

    def handle(self, *args, **options):
        self.populate_data()

    @staticmethod
    @transaction.atomic
    def populate_data():
        # Sample data for Famille
        famille_data = [
            "ALCON - VISION CARE",
            "BAUSCH & LOMB",
            "COOPERVISION",
            "JOHNSON & JOHNSON",
            "MENICON"
        ]

        # Populate Famille
        for famille_name in famille_data:
            Famille.objects.get_or_create(famille=famille_name)

        # Sample data for Produit using Faker
        produit_data = []
        for i in range(1, 20):  # Adjust the range based on how many products you want
            famille_instance = Famille.objects.get(famille=fake.random_element(famille_data))
            words = fake.words(nb=3)  # Generate a list of 3 words
            designation = ' '.join(words) 
            
            produit_info = {
                'designation' : designation,
                "famille": famille_instance,
                "conditionnement_count": fake.random_int(min=1, max=10),
                "prix": fake.random.uniform(5, 50),
            }
            produit_data.append(produit_info)

        # Populate Produit
        for produit_info in produit_data:
            Produit.objects.create(**produit_info)
