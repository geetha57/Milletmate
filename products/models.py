from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class MilletProduct(models.Model):
    MILLET_TYPES = [
        ('ragi', _('Ragi (Finger Millet)')),
        ('jowar', _('Jowar (Sorghum)')),
        ('bajra', _('Bajra (Pearl Millet)')),
        ('foxtail', _('Foxtail Millet')),
        ('proso', _('Proso Millet')),
        ('little', _('Little Millet')),
    ]

    UNIT_CHOICES = [
        ('kg', _('Kilograms (kg)')),
        ('quintal', _('Quintal')),
    ]

    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_request=models.CASCADE, related_name='products')
    millet_type = models.CharField(_("Millet Type"), max_length=20, choices=MILLET_TYPES)
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2)
    unit = models.CharField(_("Unit"), max_length=10, choices=UNIT_CHOICES, default='kg')
    price = models.DecimalField(_("Expected Price (per unit)"), max_digits=10, decimal_places=2)
    location = models.CharField(_("Location"), max_length=255)
    harvest_date = models.DateField(_("Harvest Date"))
    image = models.ImageField(_("Product Image"), upload_to='products/%Y/%m/%d/', blank=True, null=True)
    description = models.TextField(_("Additional Details"), blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Millet Product")
        verbose_name_plural = _("Millet Products")

    def __str__(self):
        return f"{self.get_millet_type_display()} - {self.farmer.email}"