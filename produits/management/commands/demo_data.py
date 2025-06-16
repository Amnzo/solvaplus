from django.core.management.base import BaseCommand
from produits.models import Famille, Produit
import random

class Command(BaseCommand):
    help = 'Crée des données de démonstration'
    name = 'demo_data'

    def handle(self, *args, **options):
        # Créer des familles
        familles = [
            Famille(
                nom="Électronique",
                description="Tous vos appareils électroniques préférés"
            ),
            Famille(
                nom="Mode",
                description="Les dernières tendances en vêtements et accessoires"
            ),
            Famille(
                nom="Maison",
                description="Décoration et mobilier pour votre intérieur"
            )
        ]

        for famille in familles:
            famille.save()
            self.stdout.write(self.style.SUCCESS(f'Famille {famille.nom} créée'))

        # Créer des produits
        produits = [
            Produit(
                famille=familles[0],
                nom="Smartphone X",
                description="Le dernier smartphone de la gamme avec écran OLED et triple caméra",
                prix=999.99,
                est_en_stock=True
            ),
            Produit(
                famille=familles[0],
                nom="Tablette Pro",
                description="Tablette haute performance avec stylet inclus",
                prix=799.99,
                est_en_stock=True
            ),
            Produit(
                famille=familles[1],
                nom="Robe d'été",
                description="Robe légère en coton pour l'été",
                prix=59.99,
                est_en_stock=True
            ),
            Produit(
                famille=familles[2],
                nom="Canapé d'angle",
                description="Canapé d'angle en cuir véritable",
                prix=1499.99,
                est_en_stock=True
            )
        ]

        for produit in produits:
            produit.save()
            self.stdout.write(self.style.SUCCESS(f'Produit {produit.nom} créé'))
