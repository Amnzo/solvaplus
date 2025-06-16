from django.shortcuts import render, get_object_or_404
from sherly_app.models import  Produit
from sherly_app.models import Famille
from django.views.decorators.csrf import csrf_protect
import os
from pathlib import Path

def accueil(request):
    familles = Famille.objects.all()
    print(familles)
    produits_en_vedette = Produit.objects.filter(is_active=True).order_by('id')[:6]
    
    # Obtenir l'ID de la famille de lentilles de contact
    famille_contact = Famille.objects.first()
    famille_id = famille_contact.id if famille_contact else None
    
    # Obtenir les images du slider
    media_path = Path(__file__).resolve().parent.parent / 'media' / 'slider'
    images = []
    
    # Parcourir les fichiers dans le dossier
    for filename in os.listdir(media_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append({
                'url': f'/media/slider/{filename}',
                'name': filename
            })
    
    return render(request, 'produits/accueil.html', {
        'familles': familles,
        'produits_en_vedette': produits_en_vedette,
        'famille_id': famille_id,
        'images': images
    })

@csrf_protect
def contact(request):
    return render(request, 'produits/contact.html')

def liste_produits(request, famille_id):
    famille = get_object_or_404(Famille, pk=famille_id)
    produits = Produit.objects.filter(famille=famille)
    return render(request, 'produits/liste_produits.html', {
        'famille': famille,
        'produits': produits
    })

def detail_produit(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id)
    return render(request, 'produits/detail_produit.html', {'produit': produit})

def slider(request):
    # Obtenir le chemin du dossier media/slider
    media_path = Path(__file__).resolve().parent.parent / 'media' / 'slider'
    images = []
    
    # Parcourir les fichiers dans le dossier
    for filename in os.listdir(media_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append({
                'url': f'/media/slider/{filename}',
                'name': filename
            })
    
    return render(request, 'produits/index.html', {'images': images})
