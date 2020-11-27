from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from . utils import cookieCart, cartData, guestOrder

# Create your views here.
def store(request):
    data = cartData(request)

    cartItems = data['cartItems']

    products = Product.objects.all()  #getting query sets
    context={'products' : products, 'cartItems' : cartItems}  #dictionary
    return render(request,'store/store.html',context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context={'items' : items, 'order' : order,  'cartItems' : cartItems} #items is pointing to orderitems class in models.py, passing both order and orderitems to cart
    return render(request,'store/cart.html',context)


def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context={'items' : items, 'order' : order, 'cartItems' : cartItems} 
    return render(request,'store/checkout.html',context)


def updateItem(request):
    data = json.loads(request.body)  #parsing the data as dict sent by js file in the form of string(body of the function)
    productId = data['productId']
    action = data['action']
    print("Action:",action)
    print("Productid:",productId)

    #get all details
    customer = request.user.customer 
    product = Product.objects.get(id=productId) #product we are passing in
    order, created = Order.objects.get_or_create(customer=customer,complete=False) #order of that particular customer.so pass customer
    orderItem, created = OrderItem.objects.get_or_create(order=order,product=product) #get_or_create becoz if that orderitem already exists, we simply want to change its quantity

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
        
    return JsonResponse("Item was added", safe=False)

#all models are imported

def processOrder(request):
    #print('Data : ',request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)

    else:
        customer, order = guestOrder(request, data)

    #for both type of  users
    total = float(data['form']['total']) #sent by checkout.html, form contains userFormData which contains total
    order.transaction_id = transaction_id

    #to prevent the user from manipulating total,before moving ahead, check if total is same as get_cart_total
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create( #assigning values to objects declared in models.py
            customer = customer,
            order = order,
            address = data['shipping']['address'], #sent by POST request
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        )

    return JsonResponse("payment and order completed",safe=False)


'''
get_or_create:
Returns a tuple of (object, created), where object is the retrieved or created object and created is a boolean specifying whether a new object was created.

This is meant to prevent duplicate objects from being created when requests are made in parallel, and as a shortcut to boilerplatish code. For example:

try:
    obj = Person.objects.get(first_name='John', last_name='Lennon')
except Person.DoesNotExist:
    obj = Person(first_name='John', last_name='Lennon', birthday=date(1940, 10, 9))
    obj.save()
'''