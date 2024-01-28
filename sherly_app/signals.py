# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Bon_Livraison
from .tasks import generate_and_send_bl_pdf

@receiver(post_save, sender=Bon_Livraison)
def schedule_pdf_generation(sender, instance, created, **kwargs):
    if created:
        eta_time = instance.date_de_bl.replace(hour=15, minute=25, second=0, microsecond=0)
        # Schedule the task to run at the time specified by date_de_bl
        #generate_and_send_bl_pdf.apply_async(args=[instance.id], eta=instance.date_de_bl)
        print("shudlingg-----------------------------------")
        generate_and_send_bl_pdf.apply_async(args=[instance.id], eta=eta_time)
