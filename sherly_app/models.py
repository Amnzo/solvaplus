from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
import random
import string
from django.utils.translation import gettext_lazy as _
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
    nif=models.CharField(max_length=100,blank=True,null=True,default='NIF:B062835052-Nº IVA : ESB068350201152')
    phrase=models.CharField(max_length=100,default="L'expédition s'effectue conformément a nos conditions générales de vente")
    pays=models.CharField(max_length=100,default="ESPAGNE")
    telephone=models.CharField(max_length=100,default="+333333333333")
    tva = models.IntegerField(default=0)

    boite_envoi = models.CharField(max_length=100,default="gestionrecrutement@hotmail.com", error_messages={'invalid': "L'adresse email de boite d'envoi est invalide."})
    boite_reception = models.CharField(max_length=100,default="optiquejaures@hotmail.com", error_messages={'invalid': "L'adresse email de boite de réception est invalide."})
    pdf_pwd=models.CharField(max_length=20,default="Optical2024")
    def __str__(self):
        return f"{self.id}"

# Create your models here.
from ckeditor.fields import RichTextField
class Famille(models.Model):
    famille = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)  # champ riche texte + image
    is_active = models.BooleanField(default=True)  # Boolean field for activation status
    image = models.ImageField(_('Image'), upload_to='familles/', blank=True)
    # Other fields for the Family model can be added here

    def __str__(self):
        return self.famille

class Produit(models.Model):
    # Déclaration des champs
    designation = models.CharField(max_length=255, blank=True, null=True)
    famille = models.ForeignKey(Famille, on_delete=models.CASCADE, blank=True, null=True)
    conditionnement_count = models.IntegerField(default=1)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=7, default='', editable=False)  # Set editable to False to prevent manual editing
    is_active = models.BooleanField(default=True)  # Boolean field for activation status
    image = models.ImageField(upload_to='produits/', blank=True, null=True)

    def generate_reference(self):
        # Générer une référence au format PXXYZZ
        random_digits = ''.join(random.choices(string.digits, k=2))
        random_letter = random.choice(string.ascii_uppercase)
        random_digits2 = ''.join(random.choices(string.digits, k=2))
        return f'P{random_digits}{random_letter}{random_digits2}'

    def save(self, *args, **kwargs):
        # Si la référence n'est pas définie, la générer
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

    def clean(self):
        # Ne valider la référence que si elle a déjà été définie.
        if self.reference:
            self.clean_reference()

    def clean_reference(self):
        reference = self.reference

        # Vérifier si la référence suit le format spécifié (PXXYZZ)
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
    axe_d = models.IntegerField()
    add_d = models.FloatField(default=0)
    quatite_d = models.IntegerField()

    categorie_g = models.ForeignKey(Famille, on_delete=models.CASCADE, related_name='commandes_g')
    produit_g = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='commandes_g')
    sphere_g = models.FloatField()
    cylindre_g = models.FloatField()
    axe_g = models.IntegerField()
    add_g = models.FloatField(default=0)
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


class Facture(models.Model):
    col1= models.CharField(max_length=20, default='Désignation')
    col2= models.CharField(max_length=20, default='Qté')
    col3= models.CharField(max_length=20, default='P.Ht')
    col4= models.CharField(max_length=20, default='% Remise')
    col5= models.CharField(max_length=20, default='Montant Remise')
    col6= models.CharField(max_length=20, default='P.U.net Ht')
    col7= models.CharField(max_length=20, default='Facture en EUR')
    col8= models.CharField(max_length=20, default='%TVA')
    facture1=models.CharField(max_length=50,blank=True,null=True,default='SCROTIS  OPTIC 2000 ')
    facture2=models.CharField(max_length=50,blank=True,null=True,default='38 rue Saint Denis')
    facture3=models.CharField(max_length=50,blank=True,null=True,default='92700 COLOMBES')
    facture4=models.CharField(max_length=50,blank=True,null=True,default='FRANCE')
    facture5=models.CharField(max_length=50,blank=True,null=True,default='Numero TVA Intraceo')
    facture6=models.CharField(max_length=50,blank=True,null=True,default='FR7547911891')
    nif_facture=models.CharField(max_length=100,blank=True,null=True,default='NIF:B062835052-Nº IVA : ESB068350201152')
    tva = models.IntegerField(blank=True,null=True,default=0)
    phrase1=models.CharField(max_length=150,blank=True,null=True,default='Indemnité forfaitaire pour frais de recouvrement en cas de retard de paiement')
    phrase2=models.CharField(max_length=150,blank=True,null=True,default='Pour effectuer le paiement, veuillez utiliser les informations bancaires suivantes :')
    paye1=models.CharField(max_length=100,blank=True,null=True,default='RIB :')
    paye2=models.CharField(max_length=100,blank=True,null=True,default='IBAN :')
    paye3=models.CharField(max_length=100,blank=True,null=True,default='BIC :')
    remarque = models.TextField(default='')
    notice=models.CharField(max_length=50,blank=True,null=True,default='REMARQUE')
    n_facture =models.CharField(max_length=50,blank=True,null=True,default='Nº FACTURE')
    date =models.CharField(max_length=50,blank=True,null=True,default='DATE')
    facture_a =models.CharField(max_length=50,blank=True,null=True,default='FACTURE A')



    def __str__(self):
        return f'Facture Numero {self.id}----{self.col1} '


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True, editable=False,default='DEFAULT_VALUE')
    mois_concerne = models.CharField(max_length=7, unique=True)  # Assuming format 'MM-YYYY'

    def __str__(self):
        return f"Invoice: {self.invoice_number}, Month: {self.mois_concerne}"

class TABLE_BL(models.Model):
    t1c1 = models.CharField(max_length=100, default='BL')  # Table 1, Colonne 1
    t1c2 = models.CharField(max_length=100, default='DATE BL')  # Table 1, Colonne 2
    t1c3 = models.CharField(max_length=100, default='CMDE')  # Table 1, Colonne 3
    t1c4 = models.CharField(max_length=100, default='DATE CMDE')  # Table 1, Colonne 4
    t1c5 = models.CharField(max_length=100, default='PORTEUR')  # Table 1, Colonne 5
    t1c6 = models.CharField(max_length=100, default='CODE CLIENT')  # Table 1, Colonne 6

    t2c1 = models.CharField(max_length=100, default='Référence')  # Table 2, Colonne 1
    t2c2 = models.CharField(max_length=100, default='Désignation')  # Table 2, Colonne 2
    t2c3 = models.CharField(max_length=100, default='Conditionnement')  # Table 2, Colonne 3
    t2c4 = models.CharField(max_length=100, default='Diamètre')  # Table 2, Colonne 4
    t2c5 = models.CharField(max_length=100, default='Rayon')  # Table 2, Colonne 5
    t2c6 = models.CharField(max_length=100, default='Sphère')  # Table 2, Colonne 6
    t2c7 = models.CharField(max_length=100, default='Cylindre')  # Table 2, Colonne 7
    t2c8 = models.CharField(max_length=100, default='Axe')  # Table 2, Colonne 8
    t2c9 = models.CharField(max_length=100, default='Oeil')  # Table 2, Co
    t2c9_g_d = models.CharField(max_length=100, default='D/G')  # Table 2, Co
    t2c10 = models.CharField(max_length=100, default='Qté')
    t2add = models.CharField(max_length=100, default='ADD')

    livre_a = models.CharField(max_length=100, default='LIVRE A')
    information_acheteur= models.CharField(max_length=100, default='INFORMATION ACHETEUR')
    date=models.CharField(max_length=100, default='DATE')








    def __str__(self):
        return "TABLE BL"

class EmailSettings(models.Model):
    EMAIL_BACKEND = models.CharField(max_length=100, default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = models.CharField(max_length=100, default='smtp.office365.com')
    EMAIL_HOST_USER = models.EmailField(default='sherylopticalstrategy@hotmail.com')
    EMAIL_HOST_PASSWORD = models.CharField(max_length=100, default='vdqlnfmsvtwsusyf')
    EMAIL_PORT = models.IntegerField(default=587)
    EMAIL_USE_TLS = models.BooleanField(default=True)
    DEFAULT_FROM_EMAIL = models.EmailField(default='sherylopticalstrategy@hotmail.com')
    SERVER_EMAIL = models.EmailField(default='sherylopticalstrategy@hotmail.com')

    def __str__(self):
        return "Email Settings"