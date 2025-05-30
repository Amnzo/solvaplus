from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.core.mail import send_mail
from sherly_app.models import Produit, Famille, Societe

def vitrine(request):
    societe = Societe.objects.first()
    familles = Famille.objects.all()
    produits = Produit.objects.filter(is_active=True).order_by('-id')[:6]
    return render(request, 'vitrine/home.html', {
        'societe': societe,
        'familles': familles,
        'produits': produits
    })

def produits_par_famille(request, famille_id):
    societe = Societe.objects.first()
    famille = get_object_or_404(Famille, id=famille_id)
    produits = Produit.objects.filter(famille=famille, is_active=True)
    
    # Paginer les produits
    paginator = Paginator(produits, 12)  # 12 produits par page
    page = request.GET.get('page')
    produits = paginator.get_page(page)
    
    return render(request, 'vitrine/produits.html', {
        'societe': societe,
        'famille': famille,
        'produits': produits
    })

def fiche_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    produits_similaires = Produit.objects.filter(famille=produit.famille).exclude(id=produit.id)[:4]
    societe = Societe.objects.first()
    
    return render(request, 'vitrine/fiche_produit.html', {
        'societe': societe,
        'produit': produit,
        'produits_similaires': produits_similaires
    })

def categories(request):
    societe = Societe.objects.first()
    familles = Famille.objects.annotate(
        nb_produits=Count('produit'),
        prix_moyen=Avg('produit__prix')
    ).order_by('famille')
    
    return render(request, 'vitrine/categories.html', {
        'societe': societe,
        'familles': familles
    })

def about(request):
    societe = Societe.objects.first()
    return render(request, 'vitrine/about.html', {
        'societe': societe
    })

def contact(request):
    societe = Societe.objects.first()
    if request.method == 'POST':
        # Traiter le formulaire de contact
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Envoyer l'email
        subject = f'Contact depuis le site - {name}'
        body = f'Nom: {name}\nEmail: {email}\nMessage: {message}'
        
        try:
            send_mail(
                subject,
                body,
                email,
                ['contact@solvaplus.com'],
                fail_silently=False,
            )
            message = 'Message envoyé avec succès !'
        except:
            message = 'Une erreur est survenue lors de l\'envoi du message.'
        
        return render(request, 'vitrine/contact.html', {
            'societe': societe,
            'message': message
        })
    
    return render(request, 'vitrine/contact.html', {
        'societe': societe
    })

def ajouter_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    # Logique pour ajouter au panier
    # Pour l'instant, on redirige vers la page du produit avec un message
    message = 'Produit ajouté au panier avec succès !'
    
    return render(request, 'vitrine/fiche_produit.html', {
        'produit': produit,
        'message': message
    })
