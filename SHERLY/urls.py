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


from .views import maintenance_page, vitrine, \
    fiche_produit, produits_par_famille  # Assurez-vous de remplacer 'project' par le nom de votre projet
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', maintenance_page, name='maintenance'),  # Route pour la page de maintenance
    path('', vitrine, name='vitrine'),  # Route pour la page de maintenance
    path('produit/<int:produit_id>/', fiche_produit, name='fiche_produit'),
    path('famille/<int:famille_id>/', produits_par_famille, name='produits_par_famille'),
    path('order_management/', include('sherly_app.urls')),  # Route pour gérer les fonctionnalités de l'application
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


