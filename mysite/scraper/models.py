from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class TrackedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    product_title = models.CharField(max_length=255)
    img_url = models.URLField()
    product_link = models.URLField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product_title
