from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path
from .views import add_categorie, add_commande, add_product, add_user, bl_custom_login, bl_custom_logout, categorie_list,commande_list, company, edit_categorie, edit_commande, edit_product, fetch_related_products, generate_pdf, list_user, products_list, test_email
from django.conf import settings
from django.conf.urls.static import static
def is_superuser(user):
    return user.is_superuser

urlpatterns = [

    #------------Famille-------------------,
    path('', login_required(categorie_list, login_url='bl_login'), name='categorie_list'),
    path('add_categorie/', user_passes_test(is_superuser, login_url='bl_login')(add_categorie), name='add_categorie'),
    path('edit_categorie/<int:id>/', user_passes_test(is_superuser, login_url='bl_login')(edit_categorie), name='edit_categorie'),
    path('fetch-related-products/', fetch_related_products, name='fetch_related_products'),
    #------------SOCIETE-------------------,
    path('company/', login_required(company, login_url='bl_login'), name='company'),
    #------------Commande-------------------,
    path('commande_list/', login_required(commande_list, login_url='bl_login'), name='commande_list'),
    path('add_commande/', login_required(add_commande, login_url='bl_login'), name='add_commande'),
    path('edit_commande/<int:bl_id>/', login_required(edit_commande, login_url='bl_login'), name='edit_commande'),

    #------------Produit-----------------------
    path('product_list', login_required(products_list, login_url='bl_login'), name='product_list'),
    path('add_product/', user_passes_test(is_superuser, login_url='bl_login')(add_product), name='add_product'),
    path('edit_product/<int:id>/', user_passes_test(is_superuser, login_url='bl_login')(edit_product), name='edit_product'),
    #------------Utilisateur-------------------,
    path('add_user/', user_passes_test(is_superuser, login_url='bl_login')(add_user), name='add_user'),
    path('list_user/', user_passes_test(is_superuser, login_url='bl_login')(list_user), name='list_user'),
    #path('generate_pdf/<int:bon_commande_id>/', EditablePDFView.as_view(), name='generate_pdf'),
    #path('generate_pdf/<int:bl_id>/', user_passes_test(is_superuser, login_url='bl_login')(generate_pdf), name='generate_pdf'),
    #path('generate_pdf/<int:bl_id>/', PDFView.as_view(), name='generate_pdf'),
    path('generate_pdf/<int:bl_id>/', user_passes_test(is_superuser, login_url='bl_login')(generate_pdf), name='page'),
    path('email/', user_passes_test(is_superuser, login_url='bl_login')(test_email), name='email'),

    path('bl_login/', bl_custom_login, name='bl_login'),
    path('bl_logout/', bl_custom_logout, name='bl_logout'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
