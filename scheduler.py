import os
import django


from django.utils import timezone
# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SHERLY.settings")

# Manually configure Django settings
django.setup()

from sherly_app.models import Bon_Livraison
import schedule
import time

from sherly_app.email_utils import send_email

def job():
    print(timezone.now())
    print("Checking Bon Livraison for today's date...")
    today = timezone.now().date()
    #bon_livraison = Bon_Livraison.objects.latest('date_de_bl')
    bon_livraisons = Bon_Livraison.objects.filter(date_de_bl__date=today, emailed=False)
    for bon_livraison in bon_livraisons:
        print("Sending email for Bon Livraison ID:", bon_livraison.id)
        send_email("http://127.0.0.1:8000", bon_livraison.id)
        bon_livraison.emailed = True
        bon_livraison.save()

    

schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)