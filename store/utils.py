import json
from . models import *

def cookieCart(request):
    try:  #get values from cookies using cookie name(here 'cart')
        cart = json.loads(request.COOKIES['cart']) #parses the cookie which is string and turns it into python dictionary
    except:
        cart = {}

    print("Cart:",cart)

    items = [] # empty list of items
    order = {'get_cart_total':0, 'get_total_cart_items':0, 'shipping':False} #manually set just temporarily
    cartItems = order['get_total_cart_items']

    for p_id in cart:
        try: #use try block to prevent items in cart that may have been removed from database itself
            cartItems += cart[p_id]['quantity']

            product = Product.objects.get(id=p_id)
            total = (product.price * cart[p_id]['quantity'])

            order['get_cart_total'] += total
            order['get_total_cart_items'] += cart[p_id]['quantity']

            item = { #create dict
                'product' : { 
                    'id' : product.id,
                    'name' : product.name,
                    'price' : product.price,
                    'imageURL' : product.imageURL
                },
                'quantity' : cart[p_id]['quantity'],
                'get_total' : total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True

        except:
            pass
    return {'items' : items, 'order' : order,  'cartItems' : cartItems}


def cartData(request):
    if request.user.is_authenticated:  #check for authenticated user
        customer = request.user.customer  #1-1 relationship
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all() #it gets all the orderitems that has this particular 'order' as parent,here child object is 'orderitem' with all lowercase
        cartItems = order.get_total_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'items' : items, 'order' : order,  'cartItems' : cartItems}


def guestOrder(request, data):
    print("User is not logged in..")
    print('COOKIES:', request.COOKIES) #Ex: COOKIES: {'csrftoken': 'N38Qx7UTqoxoefxOysxC3geLrvZ8AaBKvrw1BwgQ8AsRBeVbmuW9Te1lyAcnkUgX', 'cart': '{"2":{"quantity":1},"5":{"quantity":1}}'}

    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    #for guest user,if he has not created an acct but has shopped here,we can store his data in database so that we can know how many times he has shopped with us and some other data like items he has shopped,etc
    customer, created = Customer.objects.get_or_create(email=email) #if the email is same,we use the same customer to store data
    customer.name = name  #but the customer with above mail-id changes his name,we need to update it,so assign it outside
    customer.save()

    order = Order.objects.create(customer=customer,complete=False)

    for item in items:
        product = Product.objects.get(id=item['product']['id']) #follows from utils.py
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )

    return customer, order