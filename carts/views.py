from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


# ===================== ADD TO CART =====================
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, product=product)
    else:
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, product=product)

    for item in cart_items:
        if list(item.variation.all()) == product_variation:
            item.quantity += 1
            item.save()
            return redirect('cart')

    cart_item = CartItem.objects.create(
        product=product,
        quantity=1,
        user=request.user if request.user.is_authenticated else None,
        cart=None if request.user.is_authenticated else cart
    )
    cart_item.variation.set(product_variation)
    cart_item.save()

    return redirect('cart')

def merge_cart(request, user):
    try:
        session_cart = Cart.objects.get(cart_id=_cart_id(request))
        session_items = CartItem.objects.filter(cart=session_cart)

        for item in session_items:
            user_items = CartItem.objects.filter(user=user, product=item.product)

            for user_item in user_items:
                if list(user_item.variation.all()) == list(item.variation.all()):
                    user_item.quantity += item.quantity
                    user_item.save()
                    item.delete()
                    break
            else:
                item.user = user
                item.cart = None
                item.save()

    except Cart.DoesNotExist:
        pass


# ===================== REMOVE ONE =====================
def remove_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    cart_items = CartItem.objects.filter(product=product, cart=cart)

    for item in cart_items:
        if list(item.variation.all()) == product_variation:
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
            break

    return redirect('cart')


# ===================== DELETE ENTIRE ITEM =====================
def delete_cart_item(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    cart_items = CartItem.objects.filter(product=product, cart=cart)

    for item in cart_items:
        if list(item.variation.all()) == product_variation:
            item.delete()
            break

    return redirect('cart')


# ===================== CART PAGE =====================
def cart(request):
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0
    cart_items = []

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity

        tax = (8 * total) / 100
        grand_total = total + tax

    except Cart.DoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html',context)