# myapp/context_processors.py

from .models import Societe

def societer_info(request):
    societe = Societe.objects.first()  # Retrieve societer information (adjust as necessary)
    return {'societe': societe}
