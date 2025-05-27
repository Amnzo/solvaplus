from django.contrib import admin


from .models import *




admin.site.register(Produit)
admin.site.register(Famille)
admin.site.register(Invoice)

admin.site.register(Societe)
admin.site.register(Facture)

class Bon_CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_de_cmd', 'no_cmde')  # Add the fields you want to display in the list

admin.site.register(Bon_Commande, Bon_CommandeAdmin)

class Bon_LivraisonAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_de_bl', 'no_bl')  # Add the fields you want to display in the list

admin.site.register(Bon_Livraison, Bon_LivraisonAdmin)
admin.site.register(EmailSettings)
admin.site.register(TABLE_BL)


