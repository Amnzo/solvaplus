

import os

from django.http import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User

from SHERLY.settings import PDFKIT_CONFIG
from .forms import CompanyForm, CustomLoginForm, CustomUserRegistrationForm, ProduitForm
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
import pdfkit
from .models import Bon_Livraison, Societe  # Import your models
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
    products = Produit.objects.filter(famille=famille_id).values('id', 'designation')
    return JsonResponse(list(products), safe=False)

def fetch_related_products_in_liste(request):
    famille_id = request.GET.get('famille_id')
    print(f"famille_id {famille_id}")
    if famille_id:
    # Retrieve related products based on the selected family (or category)
        products = Produit.objects.filter(famille_id=famille_id).values(
        'reference', 'famille__famille',  'designation', 'conditionnement_count', 'prix', 'is_active', 'id')
    else:
        # Retrieve all products
        products = Produit.objects.all().values(
            'reference', 'famille__famille',  'designation', 'conditionnement_count', 'prix', 'is_active', 'id')
    print(list(products))  # Check the output in your server console
    return JsonResponse(list(products), safe=False)
#-------------------------------------------------------------------------
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

        sphere_range  = [round(x, 2) for x in [-6 + i * 0.25 for i in range(49)]]
        # Generate the range of values from -3 to +3 with a step of 0.5
        cylindre_range = [round(x, 2) for x in [-3 + i * 0.25 for i in range(25)]]

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
        #bl_data = Bon_Commande.objects.all().order_by('-date_de_cmd')
        bl_data = Bon_Commande.objects.filter(is_active=True).order_by('-date_de_cmd')

    else:
        #bl_data = Bon_Commande.objects.filter(user=request.user).order_by('-date_de_cmd')
        bl_data = Bon_Commande.objects.filter(user=request.user, is_active=True).order_by('-date_de_cmd')

    return render(request, 'commande/liste.html', {'bl_data': bl_data})

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
        quatite_d=request.POST.get('quatite_d')
        quatite_g=request.POST.get('quatite_g')
        print(date_de_bl)
        print(quatite_d)
        print(axe_d)
        print(cylindre_g)
        societe.save()
        bon_livraison.date_de_bl=date_de_bl
        bon_livraison.bon_commande.sphere_d=sphere_d
        bon_livraison.bon_commande.sphere_g=sphere_g
        bon_livraison.bon_commande.cylindre_d=cylindre_d
        bon_livraison.bon_commande.cylindre_g=cylindre_g
        bon_livraison.bon_commande.axe_d=int(float(axe_d))
        bon_livraison.bon_commande.axe_g=int(float(axe_g))
        bon_livraison.bon_commande.quatite_d=quatite_d
        bon_livraison.bon_commande.quatite_g=quatite_g
        bon_livraison.bon_commande.save()
        bon_livraison.no_bl=request.POST.get('no_bl')
        bon_livraison.save()

        return redirect('commande_list')

    else :
        bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
        return render(request,'commande/edit.html', {'bon_livraison': bon_livraison,'societe':societe})
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
        famille= Famille.objects.get(pk=form_data.get('famille'))
        active=request.POST.get('is_active')
        is_active=False
        if active=="on":
                is_active=True
        produit=Produit(
             designation=form_data.get('designation'),
             famille=famille,
             is_active=is_active,
             prix=form_data.get('prix'),
             conditionnement_count=form_data.get('conditionnement'),

        )

        produit.save()
        messages.success(request, 'Produit créé avec succes')

        return redirect('product_list')

    else:

        familles = Famille.objects.filter(is_active=True)
        return render(request,'produits/ajouter.html',{'familles':familles})

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
from .models import Bon_Livraison, Societe

def generate_pdf(request, bl_id):
    try:
        bon_livraison = Bon_Livraison.objects.get(pk=bl_id)

        societe = Societe.objects.first()

        # Read logo image file and encode it as base64
        with open(societe.logo.path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        context = {'bon_livraison': bon_livraison, 'societe': societe, 'logo_base64': logo_base64}
        html = render_to_string('pdf/telechargement.html', context)

        config = pdfkit.configuration(wkhtmltopdf=PDFKIT_CONFIG['wkhtmltopdf'])
        pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8'}, configuration=config)

        # Write the PDF content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(pdf)
            temp_file.seek(0)
            file_path = temp_file.name

        # Return the PDF file as a response for download
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bon_livraison_{bon_livraison.no_bl}.pdf"'
        return response

    except Bon_Livraison.DoesNotExist:
        logger.error("Bon Livraison not found")
        return HttpResponse("Bon Livraison not found", status=404)
    except Exception as e:
        logger.error(f"Error: {e}")
        return HttpResponse("Internal Server Error", status=500)



def generate_facture(request):

    societe = Societe.objects.first()
    with open(societe.logo.path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    bon_ids = request.GET.get('bon_ids')
    num_facture = request.GET.get('num_facture')
    date_facture = request.GET.get('date_facture')


    # Strip off square brackets and split the string
    bon_ids_list = [int(bon_id) for bon_id in bon_ids.strip('[]').split(',')]

    bons_livraison = Bon_Livraison.objects.filter(pk__in=bon_ids_list)
    context = {
        'bons_livraison':bons_livraison,
        'logo_base64':logo_base64,
        'societe': societe,
        'num_facture':num_facture,
        'date_facture':date_facture
    }
    return render(request,'facture/telechargement_facture.html', context)
    # html = render_to_string('facture/telechargement_facture.html', context)
    # config = pdfkit.configuration(wkhtmltopdf=PDFKIT_CONFIG['wkhtmltopdf'])
    # pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8'}, configuration=config)

    #     # Write the PDF content to a temporary file
    # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    #         temp_file.write(pdf)
    #         temp_file.seek(0)
    #         file_path = temp_file.name

    #     # Return the PDF file as a response for download
    # response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="Facture__{num_facture}.pdf"'
    # return response


#---------------------Facture-----------------------------


from collections import defaultdict
from datetime import datetime, timedelta



import calendar
from datetime import datetime, timedelta
from collections import defaultdict
from sherly_app.models import Bon_Livraison

def facture(request):
    aujourd_hui = datetime.now()
    premier_jour_mois_actuel = aujourd_hui.replace(day=1)

    date_dix_mois_avant = premier_jour_mois_actuel - timedelta(days=30*10)

    bons_livraison = Bon_Livraison.objects.filter(date_de_bl__gte=date_dix_mois_avant)

    bons_par_mois = defaultdict(list)
    for bon in bons_livraison:
        last_day_of_month = calendar.monthrange(bon.date_de_bl.year, bon.date_de_bl.month)[1]
        mois_concerne = bon.date_de_bl.strftime('%Y-%m-{}'.format(last_day_of_month))
        bons_par_mois[mois_concerne].append(bon.id)  # Append the ID instead of the object

    liste_factures = []
    for mois, bon_ids in bons_par_mois.items():
        mois_date = datetime.strptime(mois, '%Y-%m-%d')
        next_day = mois_date + timedelta(days=1)

        year_of_mois = mois_date.year
        month_of_mois = mois_date.month
        day_of_mois = mois_date.day
        if aujourd_hui.year == year_of_mois and aujourd_hui.month == month_of_mois:
            continue
        else:
            numero_facture = f'{mois.replace("-", "")}'
            liste_factures.append({
                'mois_concerne': mois,
                'numero_facture': f'{int(numero_facture)+90}',
                'nombre_bons': len(bon_ids),  # Use the count of IDs
                'displayed_day': next_day.strftime('%Y-%m-%d'),
                'bon_ids': bon_ids  # Pass the list of Bon_Livraison IDs
            })

    return render(request, 'facture/liste_facture.html', {'liste_factures': liste_factures})







