from django.urls import path
from . import views

app_name = 'produits'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('contact/', views.contact, name='contact'),
    path('famille/<int:famille_id>/', views.liste_produits, name='liste_produits'),
    path('produit/<int:produit_id>/', views.detail_produit, name='detail_produit'),
    path('slider/', views.slider, name='slider'),
]
