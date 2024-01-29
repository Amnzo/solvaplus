from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
import random
import string
class Societe(models.Model):
    nom1 = models.CharField(max_length=255, blank=True, null=True,default='SHERLY & STRATEGY SL')
    nom2 = models.CharField(max_length=255, blank=True, null=True,default='Division Optical')
    ligne1 = models.CharField(max_length=255, blank=True, null=True,default='AV Naciones Unidas')
    ligne2 = models.CharField(max_length=255, blank=True, null=True,default='Ed Cristamar 30,')
    ligne3 = models.CharField(max_length=255, blank=True, null=True,default='Peurto Banus 29660,')
    ligne4 = models.CharField(max_length=255, blank=True, null=True,default='Mail: admin@gmail.com')
    ligne5 = models.CharField(max_length=255, blank=True, null=True,default='Numero IVA: ESB06835052')
    logo = models.ImageField(upload_to='images/', null=True, blank=True)
    code_client = models.CharField(max_length=255,default='00033147853314')
        #-----------------livré ----------------------------
    livre1=models.CharField(max_length=50,default='SCROTIS  OPTIC 2000')
    livre2=models.CharField(max_length=50,default='38 rue Saint Denis')
    livre3=models.CharField(max_length=50,default='92700 COLOMBES')
    livre4=models.CharField(max_length=50,default='FRANCE')
    #----------------ACHTEUR------------------------
    achteur1=models.CharField(max_length=50,default='SCROTIS  OPTIC 2000 ')
    achteur2=models.CharField(max_length=50,default='38 rue Saint Denis')
    achteur3=models.CharField(max_length=50,default='92700 COLOMBES')
    achteur4=models.CharField(max_length=50,default='FRANCE')
    achteur5=models.CharField(max_length=50,default='Numero TVA Intraceo')
    achteur6=models.CharField(max_length=50,default='FR7547911891')
    nif=models.CharField(max_length=100,blank=True,null=True)
    phrase=models.CharField(max_length=100,default="L'expédition s'effectue conformément a nos conditions générales de vente")
   
    boite_envoi = models.CharField(max_length=100,default="gestionrecrutement@hotmail.com", error_messages={'invalid': "L'adresse email de boite d'envoi est invalide."})
    boite_reception = models.CharField(max_length=100,default="optiquejaures@hotmail.com", error_messages={'invalid': "L'adresse email de boite de réception est invalide."})

    def __str__(self):
        return f"{self.id}"

# Create your models here.
class Famille(models.Model):
    famille = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)  # Boolean field for activation status
    # Other fields for the Family model can be added here

    def __str__(self):
        return self.famille
    
class Produit(models.Model):
    #nom = models.CharField(max_length=50)
    designation = models.CharField(max_length=255, blank=True, null=True)
    famille = models.ForeignKey(Famille, on_delete=models.CASCADE,blank=True, null=True)
    conditionnement_count = models.IntegerField(default=1)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=7, default='', editable=False)  # Set editable to False to prevent manual editing
    is_active = models.BooleanField(default=True)  # Boolean field for activation status
    def generate_reference(self):
        # Generate a reference in the format PXXYZZ
        random_digits = ''.join(random.choices(string.digits, k=2))
        random_letter = random.choice(string.ascii_uppercase)
        random_digits2 = ''.join(random.choices(string.digits, k=2))
        return f'P{random_digits}{random_letter}{random_digits2}'

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

    def clean(self):
        # Custom validation for the reference field
        self.clean_reference()

    def clean_reference(self):
        reference = self.reference

        # Check if the reference follows the specified format (PXXYZZ)
        if not (len(reference) == 7 and
                reference[0] == 'P' and
                reference[1:3].isdigit() and
                reference[3].isalpha() and
                reference[4:6].isdigit()):
            raise ValidationError("Invalid reference format. It should be in the format PXXYZZ.")
    def __str__(self):
        return f'{self.reference} - {self.prix}'
class Bon_Commande(models.Model):
    #client = models.ForeignKey(Client, on_delete=models.CASCADE)
    client = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    categorie_d = models.ForeignKey(Famille, on_delete=models.CASCADE, related_name='commandes_d')
    produit_d = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='commandes_d')
    sphere_d = models.FloatField()
    cylindre_d = models.FloatField()
    axe_d = models.FloatField()
    quatite_d = models.IntegerField()
    
    categorie_g = models.ForeignKey(Famille, on_delete=models.CASCADE, related_name='commandes_g')
    produit_g = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='commandes_g')
    sphere_g = models.FloatField()
    cylindre_g = models.FloatField()
    axe_g = models.FloatField()
    quatite_g = models.IntegerField()
    date_de_cmd = models.DateTimeField(default=timezone.now)
    no_cmde = models.CharField(max_length=20, unique=True, editable=False,default='DEFAULT_VALUE')
    is_active=models.BooleanField(default=True)
    

    def __str__(self):
        return f'Bon_Commande for {self.client}----{self.no_cmde}----{self.id} '
    


class Bon_Livraison(models.Model):
    bon_commande = models.OneToOneField(Bon_Commande, on_delete=models.CASCADE, related_name='bon_livraison')
    date_de_bl = models.DateTimeField(default=timezone.now)
    no_bl = models.CharField(max_length=20, unique=True, editable=False,default='DEFAULT_VALUE')
    emailed = models.BooleanField(default=False)
    def __str__(self):
        return f'Bon_Livraison for {self.no_bl}----{self.id}----{self.date_de_bl} '