from django.db import models


class CompanySettings(models.Model):
    """
    Table à une seule ligne (singleton) : paramètres de l'entreprise
    (section 17 du cahier des charges).
    """
    name = models.CharField('Nom de l\'entreprise', max_length=200, default='Kamsar Street')
    logo = models.ImageField('Logo', upload_to='company/', blank=True, null=True)
    phone = models.CharField('Téléphone', max_length=40, blank=True)
    email = models.EmailField('Email', blank=True)
    address = models.CharField('Adresse', max_length=255, blank=True)
    currency = models.CharField('Devise', max_length=10, default='GNF')

    class Meta:
        db_table = 'company_settings'
        verbose_name = 'Paramètres de l\'entreprise'
        verbose_name_plural = 'Paramètres de l\'entreprise'

    def __str__(self):
        return self.name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
