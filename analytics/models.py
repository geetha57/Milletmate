from django.db import models
from django.utils.translation import gettext_lazy as _

class SalesHistory(models.Model):
    MILLET_TYPES = [
        ('ragi', _('Ragi')),
        ('jowar', _('Jowar')),
        ('bajra', _('Bajra')),
        ('foxtail', _('Foxtail')),
        ('proso', _('Proso')),
        ('little', _('Little')),
    ]

    millet_type = models.CharField(max_length=20, choices=MILLET_TYPES)
    month = models.IntegerField(_("Month (1-12)"))
    location = models.CharField(max_length=100)
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("Sales Histories")

    def __str__(self):
        return f"{self.millet_type} - {self.price} ({self.sale_date})"

class MLModelMetric(models.Model):
    """Stores model performance for Admin monitoring"""
    model_name = models.CharField(max_length=50) # e.g., 'Price Predictor'
    accuracy_score = models.FloatField()
    last_trained = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model_name}: {self.accuracy_score}%"