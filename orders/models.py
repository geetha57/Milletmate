from django.db import models
from django.conf import settings
from products.models import MilletProduct
from django.utils.translation import gettext_lazy as _

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending Verification')),
        ('accepted', _('Accepted by Farmer')),
        ('rejected', _('Rejected')),
        ('completed', _('Transaction Completed')),
    ]

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_orders')
    product = models.ForeignKey(MilletProduct, on_delete=models.CASCADE, related_name='product_orders')
    quantity = models.DecimalField(_("Order Quantity"), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_("Total Price"), max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order #{self.id} - {self.product.get_millet_type_display()}"