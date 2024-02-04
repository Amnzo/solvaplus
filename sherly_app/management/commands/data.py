from django.core.management.base import BaseCommand
from sherly_app.models import Produit

class Command(BaseCommand):
    help = 'Update product designations'

    def handle(self, *args, **options):
        self.update_product_designations()

    @staticmethod
    def update_product_designations():
        # Récupérer tous les produits
        produits = Produit.objects.all()

        # Parcourir tous les produits et mettre à jour leur désignation
        for produit in produits:
            # Supprimer "Boite de {conditionnement}" de la désignation
            produit.designation = produit.designation.replace(f" Boite de {produit.conditionnement_count}", "")
            produit.save()

        print("Product designations updated successfully.")
