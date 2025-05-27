import os
import sys
import logging

# Get the directory of the script
script_directory = os.path.dirname(os.path.abspath(__file__))
# Set the path to the log file
log_file_path = os.path.join(script_directory, 'monthly.log')

# Configure logging to write to the log file
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the directory containing the Django project to the Python path
project_root = os.path.abspath(os.path.join(script_directory, '..'))
sys.path.append(project_root)

# Set the Django settings module environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SHERLY.settings")

# Manually configure Django settings
import django
django.setup()

# Now you can import and use your Django models and settings
from SHERLY.settings import PDFKIT_CONFIG
from django.core.mail import EmailMessage
from sherly_app.models import Bon_Livraison, Facture, Societe,EmailSettings
from django.template.loader import render_to_string
import pdfkit
from django.utils import timezone
import calendar
import base64
import tempfile
from django.conf import settings  # Add this import statement
from decimal import Decimal
import PyPDF2
logging.info("---------------Starting fetching data to send by email Montly-----------------")
logging.info("---------------PREPARATION FACTURE-----------------")



def envoyer_facture():
    current_date = timezone.now()
    year = current_date.year
    month = current_date.month
    num_days_in_month = calendar.monthrange(year, month)[1]
    print("Le dernier jours de ce mois est ")
    print(num_days_in_month)
    logging.info("---------------num_days_in_month-----------------")
    logging.info(num_days_in_month)


    if current_date.day == num_days_in_month :
        facture = Facture.objects.first()
        societe = Societe.objects.first()
        first_day = timezone.datetime(year, month, 1)  # First day of the month
        last_day = current_date  # Last day of the month is today
        #bons_livraisons = Bon_Livraison.objects.filter(date_de_bl__range=(first_day, last_day))
        bons_livraisons = Bon_Livraison.objects.filter(
            date_de_bl__range=(first_day, last_day),
            bon_commande__is_active=True
        )
        total_=Decimal(0)
        for bon_livraison in bons_livraisons:
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
        formatted_date = current_date.strftime("%Y%m%d")
        numero_facture = int(formatted_date)+90
        with open(societe.logo.path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        context = {
        'bons_livraison':bons_livraisons,
        'logo_base64':logo_base64,
        'societe': societe,
        'num_facture':numero_facture,
        'date_facture':current_date.strftime("%d-%m-%Y"),
        'facture':facture,
        'total_': total_,
        'tva': tva_value,
        'total_ttc': total_ttc,
        }
        html = render_to_string('facture/telechargement_facture.html', context)
        config = pdfkit.configuration(wkhtmltopdf=PDFKIT_CONFIG['wkhtmltopdf'])
        pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8', 'disable-javascript': None, 'enable-local-file-access': ''}, configuration=config)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(pdf)
            temp_file.seek(0)
            file_path = temp_file.name
                # Set permissions to make the PDF non-editable
        writer = PyPDF2.PdfFileWriter()   #PdfFileWriter
        reader = PyPDF2.PdfFileReader(file_path)
        for page_num in range(reader.numPages):
            writer.addPage(reader.getPage(page_num))
        #writer.add_page(reader.pages[0])
        writer.encrypt('', societe.pdf_pwd, 0, True)
        with open(file_path + '_secured.pdf', 'wb') as output_file:
            writer.write(output_file)



        email_settings = EmailSettings.objects.first()
        if email_settings:
            # Assign each field to a variable
            email_backend = email_settings.EMAIL_BACKEND
            email_host = email_settings.EMAIL_HOST
            email_host_user = email_settings.EMAIL_HOST_USER
            email_host_password = email_settings.EMAIL_HOST_PASSWORD
            email_port = email_settings.EMAIL_PORT
            email_use_tls = email_settings.EMAIL_USE_TLS
            default_from_email = email_settings.DEFAULT_FROM_EMAIL
            server_email = email_settings.SERVER_EMAIL
        print(email_settings)
        settings.EMAIL_BACKEND = email_backend
        settings.EMAIL_HOST = email_host
        settings.EMAIL_HOST_USER = email_host_user
        settings.EMAIL_HOST_PASSWORD = email_host_password
        settings.EMAIL_PORT = email_port
        settings.EMAIL_USE_TLS = email_use_tls
        settings.DEFAULT_FROM_EMAIL = default_from_email
        settings.SERVER_EMAIL = server_email
        subject = f'Factura del {year}-{month}'
        #message = f'Bonjour,  Facture numero {numero_facture} envoyé depuis  SHERYL & STRATEGY SL.'
        message = f'Hola, Factura número {numero_facture} enviada desde SHERYL & STRATEGY SL.'
        #message = f'Bonjour, Ceci est un Bon de Livraison numero {bon_livraison.no_bl} envoyé depuis Django au 6eme café.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [societe.boite_reception]
        email = EmailMessage(subject, message, from_email, recipient_list)
        secured_pdf_file = open(file_path + '_secured.pdf', 'rb')
        #email.attach(f'NOTA_ENTREGA_Nº_{bon_livraison.no_bl}.pdf', secured_pdf_file.read(), 'application/pdf')
        email.attach(f'FACTURA_Nº_{numero_facture}.pdf', secured_pdf_file.read(), 'application/pdf')
        email.send()
    else:
        logging.info("-------Today is not the last day-----------------")




envoyer_facture()
