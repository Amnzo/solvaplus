import os
import sys

# Add the directory containing the Django project to the Python path
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, '..'))
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
import schedule
import time
from django.utils import timezone

def send_email(base_url, bl_id):
    print("Beginning email verification")

    try:
        bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
        print(f"Preparing BL {bon_livraison.no_bl}")
        societe = Societe.objects.first()
        logo_absolute_url = base_url + societe.logo.url 

        context = {'bon_livraison': bon_livraison, 'societe': societe, 'logo_absolute_url': logo_absolute_url}
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

        print(f"Email sent for bon de livraison {bon_livraison.no_bl}")

    except Bon_Livraison.DoesNotExist:
        print("Bon Livraison not found")


def job():
    print(timezone.now())
    print("Checking Bon Livraison for today's date...")
    today = timezone.now().date()
    bon_livraisons = Bon_Livraison.objects.filter(date_de_bl__date=today, emailed=False)
    for bon_livraison in bon_livraisons:
        print("Sending email for Bon Livraison ID:", bon_livraison.id)
        send_email("http://127.0.0.1:8000", bon_livraison.id)
        bon_livraison.emailed = True
        bon_livraison.save()

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)