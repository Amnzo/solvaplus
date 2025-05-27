

import os

from django.http import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from decimal import Decimal
from SHERLY.settings import PDFKIT_CONFIG
from .forms import CompanyForm, CustomLoginForm, CustomUserRegistrationForm, ProduitForm
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
import pdfkit
from .models import Bon_Livraison, Societe,Invoice,TABLE_BL  # Import your models
# myapp/views.py
from django.contrib.auth import authenticate, login,logout
# Create your views here.

def bl_custom_login(request):
    societe = Societe.objects.first()
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page or home page
                return redirect('categorie_list')  # Change 'home' to your actual home page URL
            else:
                # Handle invalid login
                form.add_error(None, 'Invalid login credentials')
    else:
        form = CustomLoginForm()
        societe = Societe.objects.first()

    return render(request, 'login_bl.html', {'form': form,'hide_menu': True,'societe':societe})

def bl_custom_logout(request):
    logout(request)
    # Add any additional logic or redirect as needed
    return redirect('bl_login')

#---------------------------------Famille--------------------------------------------------------
@login_required(login_url='bl_login')
def categorie_list(request):
        if request.user.is_superuser:
            familles = Famille.objects.all().order_by('famille')
            return render(request, 'categories/liste.html', {'familles': familles})
        else :
            return redirect('add_commande')

def add_categorie(request):
        if request.method == 'POST':
            famille_name = request.POST.get('famille')
            active=request.POST.get('is_active')
            is_active=False
            if active=="on":
                is_active=True

            Famille.objects.create(famille=famille_name,is_active=is_active)
            return redirect('categorie_list')  # Redirect to the category list page
        return render(request, 'categories/ajouter.html')

def edit_categorie(request,id):
        famille=Famille.objects.get(pk=id)
        if request.method == 'POST':
            print(request.POST.get('is_active'))
            famille.famille=request.POST.get('famille')
            active=request.POST.get('is_active')
            if active=="on":
                famille.is_active=True
            else :
                famille.is_active=False

            famille.save()
            return redirect('categorie_list')  # Redirect to the category list page

        return render(request, 'categories/edit_famille.html',{'famille':famille})


def fetch_related_products(request):
    famille_id = request.GET.get('famille_id')
    print(request.GET.get('famille_id'))
    # Retrieve related products based on the selected family (or category)
    products = Produit.objects.filter(famille=famille_id, is_active=True).values('id', 'designation','conditionnement_count')
    return JsonResponse(list(products), safe=False)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

def fetch_related_products_in_liste(request):
    famille_id = request.GET.get('famille_id')
    print(f"famille_id {famille_id}")

    # Filtrer les produits en fonction de la famille si elle est spécifiée
    if famille_id:
        products = Produit.objects.filter(famille_id=famille_id, is_active=True).values(
            'reference', 'famille__famille', 'designation', 'conditionnement_count', 'prix', 'is_active', 'id')
    else:
        # Si la famille n'est pas spécifiée, récupérer tous les produits actifs
        products = Produit.objects.filter(is_active=True).values(
            'reference', 'famille__famille', 'designation', 'conditionnement_count', 'prix', 'is_active', 'id')

    # Paginer les produits filtrés
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')

    try:
        products_page = paginator.page(page_number)
    except PageNotAnInteger:
        # Si le numéro de page n'est pas un entier, retourner la première page
        products_page = paginator.page(1)
    except EmptyPage:
        # Si la page demandée est vide, retourner la dernière page
        products_page = paginator.page(paginator.num_pages)

    product_list = list(products_page)

    # Calculer le nombre total de pages en fonction du nombre total de produits
    total_pages = paginator.count // 8 + (1 if paginator.count % 8 != 0 else 0)

    # Retourner la liste des produits paginés et le nombre total de pages
    return JsonResponse({'products': product_list, 'total_pages': total_pages}, safe=False)




#-------------------------------------------------------------------------
def parametrage(request):
    parametrage = EmailSettings.objects.first()
    if request.method == 'POST':
        email=request.POST.get('email')
        pwd=request.POST.get('password')

        parametrage.EMAIL_HOST_USER=email
        parametrage.EMAIL_HOST_PASSWORD=pwd
        parametrage.DEFAULT_FROM_EMAIL=email
        parametrage.SERVER_EMAIL=email
        parametrage.save()
        messages.success(request, 'LES PARAMETRE DE MESSAGRIE ON ETAIT BIEN MODIFIER')
        return redirect('company')  # Redirect to success page




    else:


        #form = EmailSettingsForm(instance=parametrage)

        return render(request, 'company/parametrage.html',{'parametrage': parametrage})

def company(request):
        societe = Societe.objects.first()
        if request.method == 'POST':
            form = CompanyForm(request.POST, request.FILES, instance=societe)
            if form.is_valid():
                form.save()
                return redirect('categorie_list')
            else:
                form = CompanyForm(request.POST,request.FILES, instance=societe)
                return render(request, 'company/edit.html', {'form': form})


        else :

            #form=CompanyForm()
            form = CompanyForm(instance=societe)  # Redirect to the category list page
        return render(request, 'company/edit.html', {'form': form})









#---------------------------------Commande--------------------------------------------------------

def next_business_day(date):
    while date.weekday() >= 5:  # Saturday or Sunday
        date += timezone.timedelta(days=1)
    return date

@login_required(login_url='bl_login')
def add_commande(request):
    if request.method == 'POST':
        form_data = request.POST.dict()

        categorie_d= Famille.objects.get(pk=form_data.get('categorie_d'))
        produit_d = Produit.objects.get(pk=form_data.get('produit_d'))
        categorie_g= Famille.objects.get(pk=form_data.get('categorie_g'))
        produit_g = Produit.objects.get(pk=form_data.get('produit_g'))
        date_part = timezone.now().strftime('%Y%m%d')
        last_bon_commande = Bon_Commande.objects.last()
        padded_id = f"{(last_bon_commande.id * last_bon_commande.id) + last_bon_commande.id}" if last_bon_commande else "1"
        no_cmde = f"{date_part}{padded_id}"
        bon_commande = Bon_Commande(client=form_data.get('client'),
                        categorie_d=categorie_d,categorie_g=categorie_g,
                        produit_d=produit_d,produit_g =produit_g,
                        sphere_d=form_data.get('sphere_d'),sphere_g=form_data.get('sphere_g'),
                        cylindre_d=form_data.get('cylindre_d'),cylindre_g=form_data.get('cylindre_g'),
                        axe_d=form_data.get('axe_d'),axe_g=form_data.get('axe_g'),
                        add_d=form_data.get('add_d'),add_g=form_data.get('add_g'),
                        quatite_d=form_data.get('quatite_d'),quatite_g=form_data.get('quatite_g'),
                        user=request.user,
                        no_cmde=no_cmde,

                           )
        bon_commande.save()
        next_day = timezone.now() + timezone.timedelta(days=1)
        next_valid_day = next_business_day(next_day.date())
        last_bon_livraison = Bon_Livraison.objects.last()
        padded_id = f"{(last_bon_livraison.id * last_bon_livraison.id)*2}" if last_bon_livraison else "1"
        date_part = next_valid_day.strftime('%Y%m%d')
        no_bl = f"{date_part}{padded_id}"
        Bon_Livraison.objects.create(
            bon_commande=bon_commande,
            date_de_bl=next_valid_day,
            no_bl=no_bl,
            # You may need to handle no_bl generation here as per your logic
        )

        messages.success(request, 'Commande créé avec succes')
        return redirect('commande_list')
    else:

        #sphere_range = [round(x, 2) for x in range(-600/100, 601/100, 5/100)]

        #sphere_range  = [round(x, 2) for x in [-6 + i * 0.25 for i in range(49)]]
        sphere_range = [round(x, 2) for x in [-12 + i * 0.25 for i in range(97)]]

        # Generate the range of values from -3 to +3 with a step of 0.5
        cylindre_range = [round(x, 2) for x in [-6 + i * 0.25 for i in range(49)]]


        # Generate the range of values from 0 to 180 with a step of 5
        axe_range = [round(x, 2) for x in range(0, 181, 5)]
        quantite_range = [round(x, 2) for x in range(1, 51, 1)]
        categories = Famille.objects.filter(is_active=True)
        products = Produit.objects.all()

        context = {

            'sphere_range': sphere_range,
            'cylindre_range':cylindre_range,
            'axe_range': axe_range,
            'quantite_range':quantite_range,
            'categories':categories,
            'products':products,



            # ... other context data
        }
        return render(request,'commande/ajouter.html', context)

@login_required(login_url='bl_login')
def commande_list(request):
    if request.user.is_superuser:
        bl_data = Bon_Commande.objects.filter(is_active=True).order_by('-date_de_cmd')
    else:
        bl_data = Bon_Commande.objects.filter(user=request.user, is_active=True).order_by('-date_de_cmd')
    items_per_page = 8
    paginator = Paginator(bl_data, items_per_page)
    page = request.GET.get('page')
    try:
        # Get the Page object for the requested page
        bl_data = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        bl_data = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, show the last page
        bl_data = paginator.page(paginator.num_pages)

    return render(request, 'commande/liste.html', {'bl_data': bl_data})

def deleted_commande(request):
    if request.user.is_superuser:
        #bl_data = Bon_Commande.objects.all().order_by('-date_de_cmd')
        bl_data = Bon_Commande.objects.filter(is_active=False).order_by('-date_de_cmd')

    return render(request, 'commande/deleted_.html', {'bl_data': bl_data})

def delete_confirmation(request,id):
    bon_commande=Bon_Commande.objects.get(pk=id)
    context = { 'bon_commande':bon_commande}
    return render(request,'commande/confirmation.html',context)
def delete_commande(request, id):
    # Récupérer la commande à supprimer
    commande = Bon_Commande.objects.get(id=id)
    print(id)
    commande.is_active=False
    # Supprimer la commande
    commande.save()
    # Redirection vers la liste des commandes
    return redirect('commande_list')
    #------------------------------------------------------

from django.core.mail import send_mail, EmailMessage
from django.conf import settings



def generate_pdf333(request, bl_id):
    try:
        bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
        societe = Societe.objects.first()
        logo_absolute_url = request.build_absolute_uri(societe.logo.url)
        context = {'bon_livraison': bon_livraison, 'societe': societe,'logo_absolute_url': logo_absolute_url}
        #return render(request,'pdf/pdf.html',context)
        html = render(request, 'pdf/pdf.html', context).content
        html_str = html.decode('utf-8')
        #config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        config = pdfkit.configuration(wkhtmltopdf=PDFKIT_CONFIG['wkhtmltopdf'])


        pdf = pdfkit.from_string(html_str, False, options={'encoding': 'UTF-8', 'enable-local-file-access': ''}, configuration=config)
        # subject = f'bon de livraison numero {bon_livraison.no_bl}'
        # message = f' Bonjour , Ceci est un Bon de Livraison numero {bon_livraison.no_bl} envoyé depuis Django au 6eme café.'
        # from_email = 'optiquejaures@hotmail.com'
        # recipient_list = ['salmi.ensa.ilsi@gmail.com','gestionrecrutement@hotmail.com']
        # email = EmailMessage(subject, message, from_email, recipient_list)
        # email.attach(f'bon_livraison_{bon_livraison.no_bl}.pdf', pdf, 'application/pdf')
        # email.send()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=bon_livraison_{bl_id}.pdf'
        #print(response)
        return response

    except Bon_Livraison.DoesNotExist:
        return HttpResponse("Bon Livraison not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)





  #----------------------------------------------



def edit_commande(request,bl_id):
    bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
    societe = Societe.objects.first()
    table_bl=TABLE_BL.objects.first()
    print(societe)

    if request.method == 'POST':
        societe.livre1= request.POST.get('livre1')
        societe.livre2= request.POST.get('livre2')
        societe.livre3= request.POST.get('livre3')
        societe.livre4= request.POST.get('livre4')
        #------------LIVREUR
        societe.achteur1= request.POST.get('achteur1')
        societe.achteur2= request.POST.get('achteur2')
        societe.achteur3= request.POST.get('achteur3')
        societe.achteur4= request.POST.get('achteur4')
        societe.achteur5= request.POST.get('achteur5')
        societe.achteur6= request.POST.get('achteur6')
        societe.phrase= request.POST.get('phrase')
        societe.nif= request.POST.get('nif')
        societe.code_client=request.POST.get('code_client')

        date_de_bl=request.POST.get('date_de_bl')
        no_bl=request.POST.get('no_bl')
        sphere_d=request.POST.get('sphere_d')
        sphere_g=request.POST.get('sphere_g')
        cylindre_d=request.POST.get('cylindre_d')
        cylindre_g=request.POST.get('cylindre_g')
        axe_d=request.POST.get('axe_d')
        axe_g=request.POST.get('axe_g')
        add_d=request.POST.get('add_d')
        add_g=request.POST.get('add_g')

        quatite_d=request.POST.get('quatite_d')
        quatite_g=request.POST.get('quatite_g')
        print(date_de_bl)
        print(quatite_d)
        print(axe_d)
        print(cylindre_g)
        societe.save()
        date_de_cmd=request.POST.get('date_de_cmd')
        no_cmde=request.POST.get('no_cmde')
        bon_livraison.date_de_bl=date_de_bl
        table_bl.t2c1 = request.POST.get('t2c1', '')  # Remplacez 't2c1' par le nom du champ de formulaire correspondant
        table_bl.t2c2 = request.POST.get('t2c2', '')  # Remplacez 't2c2' par le nom du champ de formulaire correspondant
        table_bl.t2c3 = request.POST.get('t2c3', '')  # Remplacez 't2c3' par le nom du champ de formulaire correspondant
        table_bl.t2c4 = request.POST.get('t2c4', '')  # Remplacez 't2c4' par le nom du champ de formulaire correspondant
        table_bl.t2c5 = request.POST.get('t2c5', '')  # Remplacez 't2c5' par le nom du champ de formulaire correspondant
        table_bl.t2c6 = request.POST.get('t2c6', '')  # Remplacez 't2c6' par le nom du champ de formulaire correspondant
        table_bl.t2c7 = request.POST.get('t2c7', '')  # Remplacez 't2c7' par le nom du champ de formulaire correspondant
        table_bl.t2c8 = request.POST.get('t2c8', '')  # Remplacez 't2c8' par le nom du champ de formulaire correspondant
        table_bl.t2add = request.POST.get('t2add', '')
        table_bl.t2c9 = request.POST.get('t2c9', '')  # Remplacez 't2c9' par le nom du champ de formulaire correspondant
        table_bl.t2c10 = request.POST.get('t2c10', '')  # Remplacez 't2c10' par le nom du champ de formulaire correspondant
        table_bl.t2c9_g_d = request.POST.get('t2c9_g_d', '')
        table_bl.t1c1 = request.POST.get('t1c1', '')
        table_bl.t1c2 = request.POST.get('t1c2', '')
        table_bl.t1c3 = request.POST.get('t1c3', '')
        table_bl.t1c4 = request.POST.get('t1c4', '')
        table_bl.t1c5 = request.POST.get('t1c5', '')
        table_bl.t1c6 = request.POST.get('t1c6', '')
        table_bl.information_acheteur = request.POST.get('information_acheteur', '')
        table_bl.date = request.POST.get('date', '')
        table_bl.livre_a = request.POST.get('livre_a', '')

        table_bl.save()




        bon_livraison.bon_commande.sphere_d=sphere_d
        bon_livraison.bon_commande.sphere_g=sphere_g
        bon_livraison.bon_commande.add_d=add_d
        bon_livraison.bon_commande.add_g=add_g
        bon_livraison.bon_commande.client=request.POST.get('client')
        bon_livraison.bon_commande.cylindre_d=cylindre_d
        bon_livraison.bon_commande.cylindre_g=cylindre_g
        bon_livraison.bon_commande.axe_d=int(float(axe_d))
        bon_livraison.bon_commande.axe_g=int(float(axe_g))
        bon_livraison.bon_commande.quatite_d=quatite_d
        bon_livraison.bon_commande.quatite_g=quatite_g
        bon_livraison.bon_commande.date_de_cmd=date_de_cmd
        bon_livraison.bon_commande.no_cmde=no_cmde
        bon_livraison.bon_commande.save()
        bon_livraison.no_bl=request.POST.get('no_bl')
        bon_livraison.save()

        return redirect('commande_list')

    else :
        bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
        return render(request,'commande/edit.html', {'bon_livraison': bon_livraison,'societe':societe,'table':table_bl})
#-------------------------------------------PDF------------------------------------
 # Send the email with the PDF attachment
    # subject = 'Your Bon de Livraison'
    # message = 'Thank you for your order. Please find your Bon de Livraison attached.'
    # from_email = 'salmi.ensa.ilsi@gmail.com'  # Replace with your email address
    # to_email = 'salmi.ensa.ilsi@gmail.com'  # Replace with the recipient's email address

    # email = EmailMessage(subject, message, from_email, [to_email])
    # email.attach(f'{bon_livraison.id}_bon_livraison.pdf', response.getvalue(), 'application/pdf')
    # email.send()

    #return HttpResponse('Email sent with PDF attachment.')


#---------------------------------Produit-------------------------------------------------------

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger





@login_required(login_url='bl_login')
def products_list(request):
    products = Produit.objects.all().order_by('designation')
    famille_list = Famille.objects.filter(is_active=True)

    # Set the number of items per page
    items_per_page = 8

    # Create a Paginator instance
    paginator = Paginator(products, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the Page object for the requested page
        products = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        products = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, show the last page
        products = paginator.page(paginator.num_pages)

    return render(request, 'produits/liste.html', {'products': products,'famille_list':famille_list})

def edit_product(request,id):
    product = Produit.objects.get(pk=id)
    if request.method == 'POST':
        form_data = request.POST.dict()
        famille= Famille.objects.get(pk=form_data.get('famille'))
        product.designation=form_data.get('designation')
        if request.POST.get('is_active')=="on":
            product.is_active=True
        else :
            product.is_active=False
        product.famille=famille
        product.prix=form_data.get('prix')
        product.conditionnement_count=form_data.get('conditionnement')
        product.save()
        messages.success(request, 'Produit Modifié avec succes')
        return redirect('product_list')
    familles = Famille.objects.all()
    return render(request,'produits/edit_product.html',{'familles':familles,'product':product})




def add_product(request):
    if request.method == 'POST':
        form_data = request.POST.dict()
        famille = Famille.objects.get(pk=form_data.get('famille'))
        active = request.POST.get('is_active')
        is_active = active == "on"

        # Handle image upload
        image = request.FILES.get('image')
        if not image:
            messages.error(request, "Veuillez sélectionner une image.")

        produit = Produit(
            designation=form_data.get('designation'),
            famille=famille,
            is_active=is_active,
            prix=form_data.get('prix'),
            conditionnement_count=form_data.get('conditionnement'),
            image=image  # Store the uploaded image
        )

        produit.save()
        messages.success(request, 'Produit créé avec succès')

        return redirect('product_list')

    else:
        familles = Famille.objects.filter(is_active=True)
        return render(request, 'produits/ajouter.html', {'familles': familles})


def hotmail(request):
    print("Try to send to hotmail")
    subject = 'Subject here from chdlol lmdlol'
    message = 'Here is the message.'
    from_email = 'aslal-salmi@hotmail.fr'
    recipient_list = ['salmi.ensa.ilsi@gmail.com']

    try:
        print("Recipient List:", recipient_list)  # Check the value of recipient_list
        send_mail(subject, message, from_email, recipient_list)
        return HttpResponse("Email sent successfully.")
    except Exception as e:
        return HttpResponse(f"Email sending failed because offff: {str(e)}")



def test_email(request):
    subject = 'Test Email'
    message = 'This is a test email from Django.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['recipient@example.com']

    send_mail(subject, message, from_email, recipient_list)

    return HttpResponse("Test email sent successfully.")

#---------------------------------UTILISATEUR-------------------------------------------------------
def list_user(request):
        users = User.objects.filter(is_superuser=False).order_by('-id')
        return render(request, 'utilisateurs/liste_user.html', {'users': users})



def add_user(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(username=username,password=password)
            messages.success(request, 'UTILISATEUR créé avec succes')

            # Redirect to a success page or login the user, etc.
            return redirect('list_user')

    else:
        form = CustomUserRegistrationForm()

    return render(request, 'utilisateurs/ajouter.html', {'form': form})



def profile(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            request.user.username = username
            request.user.set_password(password)  # Use set_password to securely update the password
            request.user.save()
            messages.success(request, "PROFILE ADMINISTRATEUR CHANGÉ AVEC SUCCÈS")
            return redirect('list_user')
    else:
        form = CustomUserRegistrationForm()  # Moved form instantiation inside the else block

    return render(request, 'utilisateurs/profile.html', {'form': form})


from django.contrib.auth import get_user_model
def profile_user(request, id):
    profile = User.objects.get(id=id)

    if request.method == 'POST':
        is_active=False
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            print("inside form validation")
            active=request.POST.get('is_active')
            print(active)
            if active=="on":
                is_active=True
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            profile.username = username
            profile.set_password(password)
            profile.is_active=is_active
            profile.save()
            messages.success(request, f"LE PROFILE DE {profile.username} CHANGÉ AVEC SUCCÈS")
            return redirect('list_user')
    else:
        form = CustomUserRegistrationForm()  # Pass profile as instance

    return render(request, 'utilisateurs/profile_user.html', {'form': form, 'profile': profile})



import base64
import tempfile
import pdfkit
from django.http import HttpResponse, FileResponse
from django.template.loader import render_to_string
from django.urls import reverse
from .models import Bon_Livraison, Societe,Facture
import PyPDF2
import base64
import os
import tempfile

from django.http import HttpResponse, FileResponse
from django.template.loader import render_to_string
from .models import Bon_Livraison, Societe, TABLE_BL
import pdfkit

def generate_pdf(request, bl_id):
    print("tayifihgfegkjkgkgkgbkjkbgkbkbgkdbgbdbigbidbgidbgidi")
    try:


        bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
        societe = Societe.objects.first()
        table_bl = TABLE_BL.objects.first()

        # Read logo image file and encode it as base64

        if societe.logo and societe.logo.path and os.path.exists(societe.logo.path):

            with open(societe.logo.path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            logo_base64 = None  # ou une image par défaut


        context = {'bon_livraison': bon_livraison, 'societe': societe, 'logo_base64': logo_base64, 'table': table_bl}
        html = render_to_string('pdf/telechargement.html', context)

        config = pdfkit.configuration(wkhtmltopdf=PDFKIT_CONFIG['wkhtmltopdf'])
        pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8'}, configuration=config)


        # Write the PDF content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(pdf)
            temp_file.seek(0)
            file_path = temp_file.name

        # Set permissions to make the PDF non-editable
        writer = PyPDF2.PdfWriter()
        reader = PyPDF2.PdfReader(file_path)
        writer.add_page(reader.pages[0])
        #writer.set_pdf_writer_version(PyPDF2.PdfWriter.VERSION_1_7)
        writer.encrypt(  '', societe.pdf_pwd, 0, True)

        # Write the PDF to a new file
        with open(file_path + '_secured.pdf', 'wb') as output_file:
            writer.write(output_file)


        # Return the secured PDF file as a response for download
        response = FileResponse(open(file_path + '_secured.pdf', 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="NOTA_ENTREGA_Nº_{bon_livraison.no_bl}.pdf"'
        return response

    except Bon_Livraison.DoesNotExist:
        return HttpResponse("Bon Livraison not found", status=404)
    except Exception as e:
        return HttpResponse("Internal Server Error", status=500)



def edit_facture(request):
    facture = Facture.objects.first()
    invoice_id = int(request.GET.get('invoice_id'))
    invoice = Invoice.objects.get(pk=invoice_id)
    if request.method == 'POST':
        facture.col1=request.POST.get('col1')
        facture.col2=request.POST.get('col2')
        facture.col3=request.POST.get('col3')
        facture.col4=request.POST.get('col4')
        facture.col5=request.POST.get('col5')
        facture.col6=request.POST.get('col6')
        facture.col7=request.POST.get('col7')
        facture.col8=request.POST.get('col8')
        facture.facture1=request.POST.get('facture1')
        facture.facture2=request.POST.get('facture2')
        facture.facture3=request.POST.get('facture3')
        facture.facture4=request.POST.get('facture4')
        facture.facture5=request.POST.get('facture5')
        facture.facture6=request.POST.get('facture6')
        facture.phrase1=request.POST.get('phrase1')
        facture.phrase2=request.POST.get('phrase2')
        facture.paye1=request.POST.get('paye1')
        facture.paye2=request.POST.get('paye2')
        facture.paye3=request.POST.get('paye3')
        facture.remarque=request.POST.get('remarque')
        facture.notice=request.POST.get('notice')
        facture.date=request.POST.get('date')
        facture.facture_a=request.POST.get('facture_a')
        facture.n_facture=request.POST.get('n_facture')

        facture.save()
        invoice.invoice_number=request.POST.get('num_facture')
        invoice.save()






        return redirect('facture')
    else :

        societe = Societe.objects.first()



        if societe.logo and societe.logo.path and os.path.exists(societe.logo.path):
            with open(societe.logo.path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            logo_base64 = None  # ou une image par défaut
        bon_ids = request.GET.get('bon_ids')
        num_facture = request.GET.get('num_facture')
        date_facture = request.GET.get('date_facture')
        bon_ids_list = [int(bon_id) for bon_id in bon_ids.strip('[]').split(',')]

        bons_livraison = Bon_Livraison.objects.filter(pk__in=bon_ids_list)
        facture.col1 = facture.col1.strip() if facture.col1 else ''
        facture.col2 = facture.col2.strip() if facture.col2 else ''
        facture.col3 = facture.col3.strip() if facture.col3 else ''
        facture.col4 = facture.col4.strip() if facture.col4 else ''
        facture.col5 = facture.col5.strip() if facture.col5 else ''
        facture.col6 = facture.col6.strip() if facture.col6 else ''
        facture.col7 = facture.col7.strip() if facture.col7 else ''
        facture.col8 = facture.col8.strip() if facture.col8 else ''
        context = {
            'bons_livraison':bons_livraison,
            'logo_base64':logo_base64,
            'societe': societe,
            'num_facture':num_facture,
            'date_facture':date_facture,
            'facture':facture,
            'invoice':invoice,
        }

        return render(request,'facture/edit_facture.html', context)

def generate_facture(request):
    facture = Facture.objects.first()
    societe = Societe.objects.first()
    bon_ids = request.GET.get('bon_ids')
    num_facture = request.GET.get('num_facture')
    date_facture = request.GET.get('date_facture')


    if societe.logo and societe.logo.path and os.path.exists(societe.logo.path):
        with open(societe.logo.path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    else:
        logo_base64 = None  # Ou une valeur par défaut



    # Parse date_facture to a datetime object assuming it's in the format 'DD-MM-YYYY'
    date_facture_obj = datetime.strptime(date_facture, "%d-%m-%Y")

    # Format the date object to 'YYYY-MM-DD'
    formatted_date = date_facture_obj.strftime("%Y-%m-%d")


    # Strip off square brackets and split the string
    bon_ids_list = [int(bon_id) for bon_id in bon_ids.strip('[]').split(',')]
    total_=Decimal(0)
    bons_livraison = Bon_Livraison.objects.filter(pk__in=bon_ids_list)
    for bon_livraison in bons_livraison:
        total_ += (bon_livraison.bon_commande.produit_d.prix * bon_livraison.bon_commande.quatite_d)+(bon_livraison.bon_commande.produit_g.prix * bon_livraison.bon_commande.quatite_g)
    tva_value = Decimal(0)
    total_ = round(total_, 2)
    if societe.tva != 0:
        tva_value = Decimal(societe.tva) / 100

    if tva_value != Decimal(0):
        tva_value = total_ * tva_value
        total_ttc = total_ + tva_value
        tva_value = round(tva_value, 2)
        total_ttc = round(total_ttc, 2)
    else:
        total_ttc = total_

    context = {
        'bons_livraison': bons_livraison,
        'logo_base64': logo_base64,
        'societe': societe,
        'num_facture': num_facture,
        'date_facture': date_facture_obj.strftime('%d-%m-%Y'), #Feb. 23, 2024, midnight
        'facture': facture,
        'total_': total_,
        'tva': tva_value,
        'total_ttc': total_ttc,
    }
    #return render(request,'facture/telechargement_facture.html', context)
    html = render_to_string('facture/telechargement_facture.html', context)
    config = pdfkit.configuration(wkhtmltopdf=PDFKIT_CONFIG['wkhtmltopdf'])
    pdf_file_paths = []

    # Generate individual PDF files for each page
    pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8'}, configuration=config)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf)
        temp_file.seek(0)
        pdf_file_paths.append(temp_file.name)

    # Merge the individual PDF files into one
    output_pdf_path = tempfile.NamedTemporaryFile(delete=False).name
    writer = PyPDF2.PdfWriter()
    for pdf_file_path in pdf_file_paths:
        reader = PyPDF2.PdfReader(pdf_file_path)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)

    # Encrypt the merged PDF
    writer.encrypt('', societe.pdf_pwd, 0, True)

    # Write the PDF to a new file
    with open(output_pdf_path + '_secured.pdf', 'wb') as output_file:
        writer.write(output_file)

    # Return the secured PDF file as a response for download
    response = FileResponse(open(output_pdf_path + '_secured.pdf', 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="FACTURA_Nº_{num_facture}.pdf"'
    return response

#---------------------Facture-----------------------------


from collections import defaultdict
from datetime import datetime, timedelta



import calendar
from datetime import datetime, timedelta
from collections import defaultdict
from sherly_app.models import Bon_Livraison

def facture(request):
    print("****************************************************************************************************")
    print("****************************************************************************************************")
    print("****************************************************************************************************")
    aujourd_hui = datetime.now()
    premier_jour_mois_actuel = aujourd_hui.replace(day=1)

    date_dix_mois_avant = premier_jour_mois_actuel - timedelta(days=30*10)

    #bons_livraison = Bon_Livraison.objects.filter(date_de_bl__gte=date_dix_mois_avant)
    bons_livraison = Bon_Livraison.objects.filter(
    date_de_bl__gte=date_dix_mois_avant,
    bon_commande__is_active=True
)

    bons_par_mois = defaultdict(list)
    for bon in bons_livraison:
        last_day_of_month = calendar.monthrange(bon.date_de_bl.year, bon.date_de_bl.month)[1]
        mois_concerne = bon.date_de_bl.strftime('%Y-%m-{}'.format(last_day_of_month))
        bons_par_mois[mois_concerne].append(bon.id)  # Append the ID instead of the object

    liste_factures = []
    for mois, bon_ids in bons_par_mois.items():
        mois_date = datetime.strptime(mois, '%Y-%m-%d')
        year_of_mois = mois_date.year
        month_of_mois = mois_date.month
        if aujourd_hui.year == year_of_mois and aujourd_hui.month == month_of_mois:
            continue
        else:
            mois_concerne = datetime.strptime(mois[:-3], '%Y-%m').strftime('%m-%Y')
            existing_invoice = Invoice.objects.filter(mois_concerne=mois_concerne).first()
            invoice_id=0
            if not existing_invoice:
                date_part = mois_concerne.replace("-", "")
                last_invoice = Invoice.objects.last()
                padded_id = f"{(last_invoice.id * last_invoice.id) + last_invoice.id}" if last_invoice else "1"
                invoice_number = f"{date_part}{padded_id}"
                new_invoice = Invoice.objects.create(
                invoice_number=invoice_number,
                mois_concerne=mois_concerne)
                numero_facture = new_invoice.invoice_number
                invoice_id=new_invoice.id
            else :
                numero_facture = existing_invoice.invoice_number
                invoice_id=existing_invoice.id



            liste_factures.append({
                'mois_concerne': mois_concerne ,
                'numero_facture': numero_facture,
                'nombre_bons': len(bon_ids),  # Use the count of IDs
                'displayed_day': datetime.strptime(mois, '%Y-%m-%d').strftime('%d-%m-%Y'),
                'bon_ids': bon_ids,  # Pass the list of Bon_Livraison IDs
                'invoice_id':invoice_id,
            })
    print("Liste Facture")
    print(liste_factures)
    print("Fin generation des facture")

    return render(request, 'facture/liste_facture.html', {'liste_factures': liste_factures})




def periode(request):
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        # Convert start_date and end_date strings to datetime objects


        start_date = datetime.strptime(start_date, '%d-%m-%Y')
        end_date = datetime.strptime(end_date, '%d-%m-%Y')


        #bons_livraison = Bon_Livraison.objects.filter(date_de_bl__range=(start_date, end_date))
        bons_livraison = Bon_Livraison.objects.filter(date_de_bl__range=(start_date, end_date), bon_commande__is_active=True)

        bons_livraison_ids = list(bons_livraison.values_list('id', flat=True))
        print(bons_livraison)
        print(bons_livraison_ids)
        numero_facture = end_date.strftime('%Y%m%d')
        numero_facture = str(int(numero_facture) + 90)
        context = {
            'mois_concerne': end_date.strftime('%Y-%m-%d'),
            'nombre_bons': len(bons_livraison),
            'displayed_day': end_date.strftime('%d-%m-%Y'),
            'bon_ids': bons_livraison_ids,
            'numero_facture': f'{int(numero_facture)+90}',
            'start_date': start_date,
            'end_date': end_date,

        }
        return  render(request,'facture/facture_periode.html',context)
    return render(request,'facture/facture_periode.html')


from datetime import datetime
import pytz


def repartir_et_supprimer_bl():
    print("répartition des BL")

    # Utiliser pytz pour UTC
    utc = pytz.UTC

    debut_decembre = datetime(2024, 12, 1, tzinfo=utc)  # Utilisation de pytz.UTC
    fin_janvier = datetime(2025, 1, 31, 23, 59, 59, tzinfo=utc)
    debut_fevrier = datetime(2025, 2, 1, tzinfo=utc)
    fin_mars = datetime(2025, 3, 31, 23, 59, 59, tzinfo=utc)

    # Sélectionner les BL de décembre et janvier
    bl_a_repartir = Bon_Livraison.objects.filter(date_de_bl__range=(debut_decembre, fin_janvier))

    # Nombre total à répartir
    total_bl = bl_a_repartir.count()

    if total_bl == 0:
        return "Aucun Bon de Livraison à répartir."

    # Nombre de jours pour répartir
    jours_fevrier_mars = (fin_mars - debut_fevrier).days + 1

    # Supprimer les autres BL et BC associés
    Bon_Livraison.objects.exclude(date_de_bl__range=(debut_decembre, fin_janvier)).delete()
    Bon_Commande.objects.exclude(bon_livraison__date_de_bl__range=(debut_decembre, fin_janvier)).delete()

    # Répartir équitablement
    for i, bl in enumerate(bl_a_repartir):
        # Calculer une nouvelle date répartie entre février et mars
        nouvelle_date = debut_fevrier + timedelta(days=(i % jours_fevrier_mars))
        bl.date_de_bl = nouvelle_date
        bl.save()

    return f"{total_bl} Bons de Livraison répartis équitablement sur février et mars 2025."


from django.http import JsonResponse

def repartir_bl_view(request):
    message = repartir_et_supprimer_bl()
    return JsonResponse({"message": message})



from django.shortcuts import render
from .models import Produit
import random
from decimal import Decimal

def apply_balanced_discount(request):
    # Récupérer tous les produits
    produits = Produit.objects.all()

    # Initialisation des variables pour le contrôle des réductions
    total_produits = len(produits)
    discount_range = [-2, -0.3]  # Plage de réduction de -2% à -0.3%

    # Calculer les réductions de manière plus équilibrée
    discount_proportion = int(total_produits * 0.3)  # 30% des produits avec réduction maximale de -2%
    balanced_discounts = []

    # Appliquer une réduction de -2% à 30% des produits
    for _ in range(discount_proportion):
        balanced_discounts.append(-2)

    # Appliquer une réduction entre -0.3% et -1.5% aux autres produits
    for _ in range(total_produits - discount_proportion):
        balanced_discounts.append(random.uniform(-1.5, -0.3))

    # Mélanger les réductions pour les appliquer de manière aléatoire
    random.shuffle(balanced_discounts)

    # Appliquer les réductions aux produits
    for produit, discount in zip(produits, balanced_discounts):
        # Convertir la réduction en Decimal pour éviter le TypeError
        discount_decimal = Decimal(discount)  # Conversion de float à Decimal
        discounted_price = produit.prix * (1 + discount_decimal / 100)  # Appliquer la réduction
        produit.prix = round(discounted_price, 2)  # Appliquer la réduction et arrondir à 2 décimales
        produit.save()  # Sauvegarder les modifications du produit

    # Retourner une réponse après avoir mis à jour tous les produits
    return render(request, 'produits_list.html', {'produits': produits, 'discounts_applied': balanced_discounts})











