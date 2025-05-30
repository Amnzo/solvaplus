"""
URL configuration for SHERLY project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include


from .views import vitrine, fiche_produit, produits_par_famille, categories, about, contact, ajouter_panier
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', vitrine, name='vitrine'),
    path('produit/<int:produit_id>/', fiche_produit, name='fiche_produit'),
    path('famille/<int:famille_id>/', produits_par_famille, name='produits_par_famille'),
    path('categories/', categories, name='categories'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('ajouter-au-panier/<int:produit_id>/', ajouter_panier, name='ajouter_panier'),
    path('order_management/', include('sherly_app.urls')),  # Route pour gérer les fonctionnalités de l'application
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


