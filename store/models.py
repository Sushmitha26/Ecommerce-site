from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#each model is represented by a class that subclasses django.db.models.Model. 
#Each model has a number of class variables, each of which represents a database field in the model.

#on_delete needs to be setted for creating the relationship, here it means we want to delete this item when user is deleted.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) #means a user can have only one customer and a customer can have only one user
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name  #returning the string value,this is the value that comes in admin panel when we create model.


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=True) #if digital is false(set as default),then it's a physical product,so need to ship it
    image = models.ImageField(null=True, blank=True) #pillow is image processing library that allows us to add this field to our module.

    def __str__(self):
        return self.name    

    #checks if url exists,if not,returns empty string so that we don't get error even if there is no image
    @property  #property decorator,it let's us to access this as an attribute rather than method
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True) #Many-to-one relations are defined using ForeignKey field of django.db.models,i.e customer can have multiple orders, on_delete=> if customer is deleted, we don't want to delete the order, we just set the customer to null
    date_ordered = models.DateTimeField(auto_now_add=True) #It is a good practice to name the many-to-one field with the same name as the related model, lowercase. Then auto_now fields are updated to the current timestamp every time an object is saved and are therefore perfect for tracking when an object was last modified, while an auto_now_add field is saved as the current timestamp when a row is first added to the database, and is therefore perfect for tracking when it was created.
    complete = models.BooleanField(default=False) #if false,then it's an open cart and u can continue to add items(status of cart)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all() #gets all the orderitems of this particular order denoted by self.
        cart_total = sum([item.get_total for item in orderitems]) 
        return cart_total

    @property
    def get_total_cart_items(self):
        orderitems = self.orderitem_set.all() #orderitem denotes the access of class 'OrderItem' (use small caps version)
        total_items = sum([item.quantity for item in orderitems])
        return total_items

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for item in orderitems:  #item iterates through each item in OrderItem class and has access to all its attributes
            if(item.product.digital == False):
                shipping = True
        return shipping


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,null=True) #a single product can have multiple orderitems
    order = models.ForeignKey(Order, on_delete=models.SET_NULL,null=True) #a single order can have multiple orderitems
    quantity = models.IntegerField(default=0,null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True) #if an order is deleted,we still like to have shipping addr. for that customer.
    order = models.ForeignKey(Order, on_delete=models.SET_NULL,null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address





'''
null=True sets NULL (versus NOT NULL) on the column in your DB. Blank values for Django field types such as DateTimeField or ForeignKey will be stored as NULL in the DB.

blank has no effect on the database, and null controls whether the database column allows NULL values.

blank determines whether the field will be required in forms. This includes the admin and your custom forms. 
If blank=True then the field will not be required, whereas if it's False the field cannot be blank.

The combo of the two is so frequent because typically if you're going to allow a field to be blank in your form, 
you're going to also need your database to allow NULL values for that field. The exception is CharFields and TextFields, which in Django are never saved as NULL. 
Blank values are stored in the DB as an empty string ('').
Ex:
models.CharField(blank=True) # No problem, blank is stored as ''
models.CharField(null=True) # NULL allowed, but will never be set as NULL

CHAR and TEXT types are never saved as NULL by Django, so null=True is unnecessary. However, you can manually set one of these fields to None to force set it as NULL. 
If you have a scenario where that might be necessary, you should still include null=True.

null=False, blank=False: This is the default configuration and means that the value is required in all circumstances.

null=True, blank=True: This means that the field is optional in all circumstances. (As noted below, though, this is not the recommended way to make string-based fields optional.)

null=False, blank=True: This means that the form doesn't require a value but the database does. 

null=True, blank=False: This means that the form requires a value but the database doesn't

null
Field.null

If True, Django will store empty values as NULL in the database. Default is False.
Avoid using null on string-based fields such as CharField and TextField because empty string values will always be stored as empty strings, not as NULL. If a string-based field has null=True, that means it has two possible values for "no data": NULL, and the empty string. In most cases, it’s redundant to have two possible values for "no data"; the Django convention is to use the empty string, not NULL.

For both string-based and non-string-based fields, you will also need to set blank=True if you wish to permit empty values in forms, as the null parameter only affects database storage (see blank).

blank
Field.blank

If True, the field is allowed to be blank. Default is False.

Note that this is different than null. null is purely database-related, whereas blank is validation-related. 
If a field has blank=True, form validation will allow entry of an empty value. If a field has blank=False, the field will be required.
'''