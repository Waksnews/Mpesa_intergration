from django.db import models

# Create your models here.
class Payment(models.Model):
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    checkout_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    merchant_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mpesa_receipt = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        default="PENDING"
    )

    result_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    result_description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} - {self.amount} - {self.status}"