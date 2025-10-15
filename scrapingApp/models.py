from django.db import models

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=255)
    original_price = models.DecimalField(max_digits=20, decimal_places=2)
    current_price = models.DecimalField(max_digits=20, decimal_places=2)
    previous_price = models.DecimalField(max_digits=20, decimal_places=2)
    url = models.URLField(max_length=500)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    platform = models.CharField(max_length = 50)
    last_updated = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length= 50)
    sub_category = models.CharField(max_length= 50)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name
