

from django.http import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
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
            Famille.objects.create(famille=famille_name)
            return redirect('categorie_list')  # Redirect to the category list page
        return render(request, 'categories/ajouter.html')

def edit_categorie(request,id):
        famille=Famille.objects.get(pk=id)
        if request.method == 'POST':
            famille.famille=request.POST.get('famille')
            famille.save()
            return redirect('categorie_list')  # Redirect to the category list page
        
        return render(request, 'categories/edit_famille.html',{'famille':famille})


def fetch_related_products(request):
    famille_id = request.GET.get('famille_id')
    # Retrieve related products based on the selected family (or category)
    products = Produit.objects.filter(famille=famille_id).values('id', 'designation')
    return JsonResponse(list(products), safe=False)



#-------------------------------------------------------------------------
def company(request):
        societe = Societe.objects.first()
        if request.method == 'POST':
            form = CompanyForm(request.POST, request.FILES, instance=societe)
            if form.is_valid():
                form.save()
            return redirect('categorie_list')
        else :
           
            #form=CompanyForm()
            form = CompanyForm(instance=societe)  # Redirect to the category list page
        return render(request, 'company/edit.html', {'form': form})






    
#---------------------------------Commande--------------------------------------------------------


@login_required(login_url='bl_login')
def add_commande(request):
    if request.method == 'POST':
        form_data = request.POST.dict()

        categorie_d= Famille.objects.get(pk=form_data.get('categorie_d'))
        produit_d = Produit.objects.get(pk=form_data.get('produit_d'))
        categorie_g= Famille.objects.get(pk=form_data.get('categorie_g'))
        produit_g = Produit.objects.get(pk=form_data.get('produit_g'))
        bon_commande = Bon_Commande(client=form_data.get('client'),
                        categorie_d=categorie_d,categorie_g=categorie_g,
                        produit_d=produit_d,produit_g =produit_g,
                        sphere_d=form_data.get('sphere_d'),sphere_g=form_data.get('sphere_g'),
                        cylindre_d=form_data.get('cylindre_d'),cylindre_g=form_data.get('cylindre_g'),
                        axe_d=form_data.get('axe_d'),axe_g=form_data.get('axe_g'),
                        quatite_d=form_data.get('quatite_d'),quatite_g=form_data.get('quatite_g'),
                        user=request.user,

                          
                          
                           )
        bon_commande.save()
        messages.success(request, 'Bon de Commande créé avec succes')
        return redirect('commande_list')
    else:
    
        #sphere_range = [round(x, 2) for x in range(-600/100, 601/100, 5/100)]
        
        sphere_range  = [round(x, 2) for x in [-6 + i * 0.25 for i in range(49)]]
        # Generate the range of values from -3 to +3 with a step of 0.5
        cylindre_range = [round(x, 2) for x in [-3 + i * 0.25 for i in range(25)]]

        # Generate the range of values from 0 to 180 with a step of 5
        axe_range = [round(x, 2) for x in range(0, 181, 5)]
        quantite_range = [round(x, 2) for x in range(1, 51, 1)]
        categories = Famille.objects.all()
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
        bl_data = Bon_Commande.objects.all().order_by('-date_de_cmd')
    else:
        bl_data = Bon_Commande.objects.filter(user=request.user).order_by('-date_de_cmd')
    return render(request, 'commande/liste.html', {'bl_data': bl_data})
    #------------------------------------------------------


def generate_pdf(request, bl_id):
    try:
        bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
        societe = Societe.objects.first()
        logo_absolute_url = request.build_absolute_uri(societe.logo.url)
        context = {'bon_livraison': bon_livraison, 'societe': societe,'logo_absolute_url': logo_absolute_url}
        #return render(request,'pdf/pdf.html',context)
        html = render(request, 'pdf/pdf.html', context).content
        html_str = html.decode('utf-8')
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        
        pdf = pdfkit.from_string(html_str, False, options={'encoding': 'UTF-8', 'disable-javascript': None, 'enable-local-file-access': ''}, configuration=config)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=bon_livraison_{bl_id}.pdf'
        print(response)
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
        societe.save()
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
    
    # Set the number of items per page
    items_per_page = 5
    
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
    
    return render(request, 'produits/liste.html', {'products': products})

def edit_product(request,id):
    product = Produit.objects.get(pk=id)
    if request.method == 'POST':
        form_data = request.POST.dict()
        famille= Famille.objects.get(pk=form_data.get('famille'))
        product.designation=form_data.get('designation')
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
        produit=Produit(
             designation=form_data.get('designation'),
             famille=famille,
             prix=form_data.get('prix'),
             conditionnement_count=form_data.get('conditionnement'),

        )
         
        produit.save()
        messages.success(request, 'Produit créé avec succes')

        return redirect('product_list') 

    else:
        
        familles = Famille.objects.all() 
        return render(request,'produits/ajouter.html',{'familles':familles})

def test_email(request):
    subject = 'Test Email'
    message = 'This is a test email from Django.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['recipient@example.com']

    send_mail(subject, message, from_email, recipient_list)

    return HttpResponse("Test email sent successfully.")

#---------------------------------UTILISATEUR-------------------------------------------------------
def list_user(request):
        users = User.objects.all().order_by('-id')
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
