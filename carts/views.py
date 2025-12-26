from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartItem


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


# ===================== ADD TO CART =====================
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
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
            item.quantity += 1
            item.save()
            return redirect('cart')

    cart_item = CartItem.objects.create(
        product=product,
        quantity=1,
        cart=cart
    )
    if product_variation:
        cart_item.variation.set(product_variation)
    cart_item.save()

    return redirect('cart')


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
