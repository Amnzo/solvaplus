from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Famille(models.Model):
    nom = models.CharField(_('Nom'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(_('Image'), upload_to='familles/', blank=True)
    date_creation = models.DateTimeField(_('Date de création'), default=timezone.now)

    class Meta:
        verbose_name = _('Famille de produits')
        verbose_name_plural = _('Familles de produits')
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Produit(models.Model):
    famille = models.ForeignKey(Famille, on_delete=models.CASCADE, verbose_name=_('Famille'))
    nom = models.CharField(_('Nom'), max_length=200)
    description = models.TextField(_('Description'))
    image = models.ImageField(_('Image'), upload_to='produits/', default='produits/default-product.jpg')
    est_en_stock = models.BooleanField(_('En stock'), default=True)
    date_creation = models.DateTimeField(_('Date de création'), default=timezone.now)

    class Meta:
        verbose_name = _('Produit')
        verbose_name_plural = _('Produits')
        ordering = ['nom']

    def __str__(self):
        return self.nom
