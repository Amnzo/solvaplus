# your_app_name/email_utils.py

from django.core.mail import EmailMessage

from sherly_app.models import Bon_Livraison, Societe
from django.template.loader import render_to_string
import pdfkit
def send_email(base_url,bl_id):
    print("caliiing methode")
    print(f"serching bl {bl_id}")

    try:
        bon_livraison = Bon_Livraison.objects.get(pk=bl_id)
        societe = Societe.objects.first()
        logo_absolute_url = base_url + societe.logo.url 

        context = {'bon_livraison': bon_livraison, 'societe': societe, 'logo_absolute_url': logo_absolute_url}
        #html = render('pdf/pdf.html', context).content
        html = render_to_string('pdf/pdf.html', context)
        
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8', 'disable-javascript': None, 'enable-local-file-access': ''}, configuration=config)
        

        subject = f'bon de livraison numero {bon_livraison.no_bl}'
        message = f' Bonjour , Ceci est un Bon de Livraison numero {bon_livraison.no_bl} envoyé depuis Django au 6eme café.'
        from_email = 'optiquejaures@hotmail.com'
        recipient_list = ['salmi.ensa.ilsi@gmail.com', 'gestionrecrutement@hotmail.com']
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.attach(f'bon_livraison_{bon_livraison.no_bl}.pdf', pdf, 'application/pdf')
        email.send()

        # Print message to console
        print(f"Email sent for bon de livraison {bon_livraison.no_bl}")

    except Bon_Livraison.DoesNotExist:
        print("Bon Livraison not found")
