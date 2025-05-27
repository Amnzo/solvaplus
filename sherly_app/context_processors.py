# myapp/context_processors.py

from .models import Societe, Famille, Produit


def societer_info(request):
    societe = Societe.objects.first()  # Retrieve societer information (adjust as necessary)
    return {'societe': societe}
def familles_context(request):
    familles = Famille.objects.all()  # Récupère toutes les familles
    return {'familles': familles}
def produits_context(request):
    produits = Produit.objects.all()  # Récupère toutes les familles
    return {'produits': produits}
