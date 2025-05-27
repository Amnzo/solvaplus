import os
import sys
import logging

# Get the directory of the script
script_directory = os.path.dirname(os.path.abspath(__file__))
# Set the path to the log file
log_file_path = os.path.join(script_directory, 'daily.log')

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
from sherly_app.models import Bon_Livraison, Societe,EmailSettings,TABLE_BL
from django.template.loader import render_to_string
import pdfkit
import PyPDF2
import tempfile

from django.utils import timezone
import base64
from django.conf import settings  # Add this import statement
logging.info("---------------Starting fetching data to send by email-----------------")
logging.info("---------------JOB DOOR-----------------")

def job():
    logging.info("---------------INSIDE JOB-----------------")
    logging.info("Checking Bon Livraison for today's date...")
    today = timezone.now().date()
    #bon_livraisons = Bon_Livraison.objects.filter(date_de_bl__date=today, emailed=False)
    bon_livraisons = Bon_Livraison.objects.filter(date_de_bl__date=today, emailed=False, bon_commande__is_active=True)
    logging.info("---------------this is what i find ----------------")
    logging.info(bon_livraisons)


    for bon_livraison in bon_livraisons:
        logging.info(f"Sending email for Bon Livraison ID: {bon_livraison.id}")
        send_email(bon_livraison.id)
        bon_livraison.emailed = True
        bon_livraison.save()

def send_email(bl_id):
    logging.info("Beginning email verification")

    try:
        bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
        logging.info(f"Preparing BL {bon_livraison.no_bl} ")
        societe = Societe.objects.first()
        table_bl=TABLE_BL.objects.first()
        with open(societe.logo.path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        context = {'bon_livraison': bon_livraison, 'societe': societe, 'logo_base64': logo_base64,'table':table_bl}
        html = render_to_string('pdf/pdf.html', context)

        config = pdfkit.configuration(wkhtmltopdf=PDFKIT_CONFIG['wkhtmltopdf'])
        pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8', 'disable-javascript': None, 'enable-local-file-access': ''}, configuration=config)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(pdf)
            temp_file.seek(0)
            file_path = temp_file.name
                # Set permissions to make the PDF non-editable
        writer = PyPDF2.PdfFileWriter()   #PdfFileWriter
        reader = PyPDF2.PdfFileReader(file_path)
        #writer.add_page(reader.pages[0])
        writer.addPage(reader.getPage(0))



        #writer.set_pdf_writer_version(PyPDF2.PdfWriter.VERSION_1_7)
        writer.encrypt('',societe.pdf_pwd, 0, True)

        # Write the PDF to a new file
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

        # Set email backend and other settings dynamically
        settings.EMAIL_BACKEND = email_backend
        settings.EMAIL_HOST = email_host
        settings.EMAIL_HOST_USER = email_host_user
        settings.EMAIL_HOST_PASSWORD = email_host_password
        settings.EMAIL_PORT = email_port
        settings.EMAIL_USE_TLS = email_use_tls
        settings.DEFAULT_FROM_EMAIL = default_from_email
        settings.SERVER_EMAIL = server_email
        #subject = f'bon de livraison numero {bon_livraison.no_bl}'
        subject = f'Nota de entrega número {bon_livraison.no_bl}'

        #message = f'Bonjour, Ceci est un Bordereau de Livraison numero {bon_livraison.no_bl} envoyé depuis  SHERYL & STRATEGY SL.'
        message = ''

        #message = f'Bonjour, Ceci est un Bon de Livraison numero {bon_livraison.no_bl} envoyé depuis Django au 6eme café.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [societe.boite_reception]
        email = EmailMessage(subject, message, from_email, recipient_list)
        #email.attach(f'NOTA_ENTREGA_Nº_{bon_livraison.no_bl}.pdf', pdf, 'application/pdf')
        secured_pdf_file = open(file_path + '_secured.pdf', 'rb')
        email.attach(f'NOTA_ENTREGA_Nº_{bon_livraison.no_bl}.pdf', secured_pdf_file.read(), 'application/pdf')

        email.send()

        logging.info(f"Email sent for bon de livraison {bon_livraison.no_bl}")

    except Bon_Livraison.DoesNotExist:
        logging.error("Bon Livraison not found")


job()
