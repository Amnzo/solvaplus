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
from sherly_app.models import Bon_Livraison, Societe
from django.template.loader import render_to_string
import pdfkit

from django.utils import timezone
import base64

logging.info("---------------Starting fetching data to send by email-----------------")
logging.info("---------------JOB DOOR-----------------")

def job():
    logging.info("---------------INSIDE JOB-----------------")
    logging.info("Checking Bon Livraison for today's date...")
    today = timezone.now().date()
    bon_livraisons = Bon_Livraison.objects.filter(date_de_bl__date=today, emailed=False)
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
        with open(societe.logo.path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        context = {'bon_livraison': bon_livraison, 'societe': societe, 'logo_base64': logo_base64}
        html = render_to_string('pdf/pdf.html', context)

        config = pdfkit.configuration(wkhtmltopdf=PDFKIT_CONFIG['wkhtmltopdf'])
        pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8', 'disable-javascript': None, 'enable-local-file-access': ''}, configuration=config)

        subject = f'bon de livraison numero {bon_livraison.no_bl}'
        message = f'Bonjour, Ceci est un Bon de Livraison numero {bon_livraison.no_bl} envoyé depuis Django au 6eme café.'
        from_email = societe.boite_envoi
        recipient_list = ['salmi.ensa.ilsi@gmail.com', societe.boite_reception]
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.attach(f'bon_livraison_{bon_livraison.no_bl}.pdf', pdf, 'application/pdf')
        email.send()

        logging.info(f"Email sent for bon de livraison {bon_livraison.no_bl}")

    except Bon_Livraison.DoesNotExist:
        logging.error("Bon Livraison not found")


job()
