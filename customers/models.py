from django.db import models


class Customer(models.Model):
    name = models.CharField('Nom', max_length=200)
    phone = models.CharField('Téléphone', max_length=40, blank=True)
    email = models.EmailField('Email', blank=True)
    address = models.CharField('Adresse', max_length=255, blank=True)
    created_at = models.DateTimeField('Créé le', auto_now_add=True)

    class Meta:
        db_table = 'customers'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['name']

    def __str__(self):
        return self.name
