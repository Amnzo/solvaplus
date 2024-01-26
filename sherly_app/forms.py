from django import forms

from .models import Famille, Produit,Societe
class CustomLoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class ProduitForm(forms.ModelForm):
    famille = forms.ModelChoiceField(queryset=Famille.objects.all(), empty_label=None)
    class Meta:
        model = Produit
        fields = ['designation', 'famille','prix']
    
class CustomUserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)



    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')

        return password2
    
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Societe
        fields = ['nom1', 'nom2','ligne1','ligne2','ligne3','ligne4','ligne5','logo','code_client']


