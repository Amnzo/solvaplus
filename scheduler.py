import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SHERLY.settings")

# Manually configure Django settings
django.setup()

from sherly_app.models import Bon_Livraison
import schedule
import time

from sherly_app.email_utils import send_email

def job():
    print("Sending email...")
    bon_livraison = Bon_Livraison.objects.latest('date_de_bl')
    send_email("http://127.0.0.1:8000",bon_livraison.id)
    

# Schedule the job to run every minute
schedule.every().minute.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)  # Sleep for 1 second to avoid consuming too much CPU
