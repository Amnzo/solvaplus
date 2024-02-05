# your_app_name/email_utils.py

from django.core.mail import EmailMessage
from .models import Bon_Livraison, Societe
from django.template.loader import render_to_string
import os
import django


from django.utils import timezone
# Set the DJANGO_SETTINGS_MODULE environment variable
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SHERLY.settings")

# Manually configure Django settings

import time
import pdfkit
def send_email():
    print("debut  email verification ")


    try:
        today = timezone.now().date()
        bon_livraisons = Bon_Livraison.objects.filter(date_de_bl__date=today, emailed=False)
        base_url="https://karimatoka.pythonanywhere.com"
        societe = Societe.objects.first()
        #bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
        for bon_livraison in bon_livraisons: 
            logo_absolute_url = base_url + societe.logo.url 
            context = {'bon_livraison': bon_livraison, 'societe': societe, 'logo_absolute_url': logo_absolute_url}
            #html = render('pdf/pdf.html', context).content
            html = render_to_string('pdf/pdf.html', context)
            
            #config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
            config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
            pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8', 'disable-javascript': None, 'enable-local-file-access': ''}, configuration=config)
            

            subject = f'bon de livraison numero {bon_livraison.no_bl}'
            message = f' Bonjour , Ceci est un Bon de Livraison numero {bon_livraison.no_bl} envoyé depuis Django au 6eme café.'
            from_email = societe.boite_envoi
            recipient_list = ['salmi.ensa.ilsi@gmail.com', societe.boite_reception]
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.attach(f'bon_livraison_{bon_livraison.no_bl}.pdf', pdf, 'application/pdf')
            email.send()

            # Print message to console
            print(f"Email sent for bon de livraison {bon_livraison.no_bl}")
            bon_livraison.emailed = True
            bon_livraison.save()

    except Bon_Livraison.DoesNotExist:
        print("Bon Livraison not found")
