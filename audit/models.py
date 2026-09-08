from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Utilisateur', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField('Action', max_length=100)
    module = models.CharField('Module', max_length=50)
    description = models.CharField('Description', max_length=255, blank=True)
    timestamp = models.DateTimeField('Horodatage', auto_now_add=True)
    ip_address = models.GenericIPAddressField('Adresse IP', null=True, blank=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journal d'activité"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} — {self.action}"
