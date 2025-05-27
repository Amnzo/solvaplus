import random

from django.http import HttpResponse
from django.shortcuts import render

from sherly_app.models import Produit,Famille
from django.shortcuts import render, get_object_or_404


def vitrine(request):

    produits = Produit.objects.filter(is_active=True)
    return render(request, 'vitrine/index.html', {'produits': produits})

def produits_par_famille(request, famille_id):
    famille = get_object_or_404(Famille, id=famille_id)
    produits = Produit.objects.filter(famille=famille)  # Filtrer les produits

    return render(request, 'vitrine/index.html', {'produits': produits ,"famille":famille})


def fiche_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    produits_similaires = list(Produit.objects.filter(famille=produit.famille).exclude(id=produit.id))
    print(produits_similaires)


    #return(produit)
    #return render(request, '', {'produit': produit,'produits_similaires': produits_similaires})
    return render(request, 'vitrine/fiche_produit.html', {
        'produit': produit,
        'produits_similaires': produits_similaires
    })



def maintenance_page(request):
    message = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Page de maintenance</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
            }
            .maintenance-message {
                background-color: #fff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            .icon {
                width: 100px; /* Taille de l'image */
                margin-bottom: 20px; /* Espace sous l'image */
            }
        </style>
    </head>
    <body>
        <div class="maintenance-message">
            <img src="https://cdn-icons-png.flaticon.com/512/4411/4411553.png" alt="Icône de maintenance" class="icon">
            <h1>Sitio en mantenimiento</h1>
            <p>El sitio web está temporalmente en mantenimiento. Estaremos de vuelta pronto. Gracias por su paciencia.</p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(message)
