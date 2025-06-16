from django.core.management.base import BaseCommand
from produits.models import Famille, Produit
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Crée des données de démonstration pour les lentilles de contact'

    def handle(self, *args, **options):
        # Créer la famille Lentilles de Contact
        famille, created = Famille.objects.get_or_create(
            nom="Lentilles de Contact",
            description="Une large sélection de lentilles de contact de qualité"
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Famille "Lentilles de Contact" créée'))
        else:
            self.stdout.write(self.style.SUCCESS('Famille "Lentilles de Contact" mise à jour'))

        # Créer les produits
        produits = [
            {
                'nom': 'Total 30',
                'description': 'Lentilles de contact mensuelles du laboratoire Alcon',
                'prix': 44.95,
                'date_creation': datetime.now() - timedelta(days=30)
            },
            {
                'nom': 'Total 30 Multifocal',
                'description': 'Lentilles de contact mensuelles multifocales du laboratoire Alcon',
                'prix': 65.00,
                'date_creation': datetime.now() - timedelta(days=15)
            },
            {
                'nom': 'Precision 1',
                'description': 'Gamme de lentilles de contact mensuelles',
                'prix': 23.90,
                'date_creation': datetime.now() - timedelta(days=7)
            },
            {
                'nom': 'Precision 1 for Astigmatism',
                'description': 'Lentilles de contact mensuelles pour astigmatisme',
                'prix': 30.80,
                'date_creation': datetime.now() - timedelta(days=5)
            },
            {
                'nom': 'Acuvue Oasys Max 1 Day',
                'description': 'Lentilles de contact journalières de haute qualité',
                'prix': 37.90,
                'date_creation': datetime.now() - timedelta(days=3)
            },
            {
                'nom': 'Acuvue Oasys Max 1 Day Multifocal',
                'description': 'Lentilles de contact journalières multifocales',
                'prix': 49.90,
                'date_creation': datetime.now() - timedelta(days=1)
            },
            {
                'nom': 'Total 30 for Astigmatism',
                'description': 'Lentilles de contact mensuelles pour astigmatisme',
                'prix': 54.50,
                'date_creation': datetime.now() - timedelta(days=20)
            },
            {
                'nom': 'Ophtalmic HR Perfexion Progressive',
                'description': 'Lentilles de contact mensuelles progressives',
                'prix': 98.50,
                'date_creation': datetime.now() - timedelta(days=10)
            },
            {
                'nom': 'OPHTALMIC HR Perfexion RX Toric',
                'description': 'Lentilles de contact mensuelles toriques',
                'prix': 149.00,
                'date_creation': datetime.now() - timedelta(days=12)
            }
        ]

        for produit_data in produits:
            produit, created = Produit.objects.get_or_create(
                famille=famille,
                nom=produit_data['nom'],
                defaults={
                    'description': produit_data['description'],
                    'prix': produit_data['prix'],
                    'est_en_stock': True,
                    'date_creation': produit_data['date_creation']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Produit {produit.nom} créé'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Produit {produit.nom} mis à jour'))
