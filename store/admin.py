from django.contrib import admin

# Register your models here.
from .models import *  #telling to import all from .models directory and . becoz both ar in same directory

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)