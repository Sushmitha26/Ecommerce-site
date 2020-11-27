var updateBtns = document.getElementsByClassName('update-cart') //query all cart items,i.e all buttons

for(var i=0; i<updateBtns.length; i++) { //loop through all buttons
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product //query custom attribute 'product' setted in store.html of this particular item
        var action = this.dataset.action
        console.log('productId:', productId, 'Action:', action)

        console.log('USER:',user)
        if(user == 'AnonymousUser') { //builtin, given by django
            addCookieItem(productId,action)
        }else {
            updateUserOrder(productId,action)
        }
    })
}

function addCookieItem(productId,action) {
    console.log('User is not logged in')

    /*Ex of how cart looks like
    cart = {
        '1':{'quantity':4},
        '4':{'quantity':1},
        '6':{'quantity':2},
    }
     */
    if(action == 'add') {
        //if item is not in cart(ex:cart[1]), then create it,if already present,simply add to the quantity
        if(cart[productId] == undefined) {  //variable cart is in main.html
            cart[productId] = {'quantity' : 1}
        }else {
            cart[productId]['quantity'] += 1  //cookie object will contain nested objects with the id of the product being the quantity and its value
        }
    }

    if(action == 'remove') {
        cart[productId]['quantity'] -= 1 

        if(cart[productId]['quantity'] <=0) {
            console.log("Item shd be deleted")
            delete cart[productId];
        }
    }

    console.log("Cart:", cart)
    //update the cookie using the updated 'cart' object and set it to the same path
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()
}

function updateUserOrder(productId, action) {  
    console.log('User is logged in, sending data...')//send data to that updateItem() view and it'll process that
    var url = '/update_item/'  //set the url to which we want to send the post data to,Ex:POST http://127.0.0.1:8000/update_item/
    console.log("URL:",url)
    fetch(url, {  //fetch api is used to send a post request,pass the url to which we want to send the post data
        method: 'POST', //type of data u pass
        headers:{ //if sending post data,passing headers is must
            'Content-Type':'application/json', 
            'X-CSRFToken' : csrftoken, //it is from main.html
        },
        body:JSON.stringify({'productId': productId, 'action': action}) //stringify and send the data u want to send as json object 
    }) 
    .then((response) => {
        return response.json();  
    })
    .then((data) => {  //the data,i.e response.json, we got back here is that string 
        console.log('Data:',data) //promise is returned here,i.e 'Item was added'
        location.reload()  //once the new data is passed,reload it so that we can see the changes immediately
    });
}


/*
The CSRF middleware and template tag provides easy-to-use protection against Cross Site Request Forgeries. 
This type of attack occurs when a malicious website contains a link, a form button or some JavaScript that is intended to perform some action on your website,
using the credentials of a logged-in user who visits the malicious site in their browser. A related type of attack, ‘login CSRF’,
 where an attacking site tricks a user’s browser into logging into a site with someone else’s credentials, is also covered.
 
 To take advantage of CSRF protection in your views, follow these steps:

The CSRF middleware is activated by default in the MIDDLEWARE setting. If you override that setting, remember that 'django.middleware.csrf.CsrfViewMiddleware'
 should come before any view middleware that assume that CSRF attacks have been dealt with.

In any template that uses a POST form, use the csrf_token tag inside the <form> element if the form is for an internal URL, e.g.:

<form method="post">{% csrf_token %}

This should not be done for POST forms that target external URLs, since that would cause the CSRF token to be leaked, leading to a vulnerability.

AJAX:
While the above method can be used for AJAX POST requests, it has some inconveniences: 
you have to remember to pass the CSRF token in as POST data with every POST request. 
For this reason, there is an alternative method: on each XMLHttpRequest, set a custom X-CSRFToken header (as specified by the CSRF_HEADER_NAME setting) to the value of the CSRF token. 
This is often easier because many JavaScript frameworks provide hooks that allow headers to be set on every request.

The recommended source for the token is the csrftoken cookie, which will be set if you’ve enabled CSRF protection for your views as outlined above.

The CSRF token cookie is named csrftoken by default, but you can control the cookie name via the CSRF_COOKIE_NAME setting.

You can acquire the token like this:(written in main.html's script)
 */