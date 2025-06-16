from django.contrib import admin
from .models import Famille, Produit

@admin.register(Famille)
class FamilleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'date_creation')
    search_fields = ('nom', 'description')
    list_filter = ('date_creation',)
    ordering = ('nom',)
    fields = ('nom', 'description', 'image')

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'famille', 'est_en_stock', 'date_creation')
    list_filter = ('famille', 'est_en_stock', 'date_creation')
    search_fields = ('nom', 'description')
    ordering = ('nom',)
    fields = (
        'famille',
        'nom',
        'description',
        'est_en_stock',
        'image',
        'date_creation'
    )
    readonly_fields = ('date_creation',)

