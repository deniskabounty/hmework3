from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Category


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/product_detail.html', {'product': product})


def _get_cart(request):
    cart = request.session.get('cart')
    if not cart:
        cart = {'items': {}, 'total_qty': 0, 'total_sum': 0.0}
        request.session['cart'] = cart
    return cart

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    qty = int(request.POST.get('qty', 1))
    if qty < 1:
        qty = 1

    cart = _get_cart(request)
    pid = str(product.id)

    if pid in cart['items']:
        cart['items'][pid]['qty'] += qty
    else:
        cart['items'][pid] = {
            'name': product.name,
            'price': float(product.price),
            'qty': qty,
            'image': product.image.url if product.image else ''
        }


    cart['total_qty'] = sum(i['qty'] for i in cart['items'].values())
    cart['total_sum'] = sum(i['qty'] * i['price'] for i in cart['items'].values())

    _save_cart(request, cart)
    messages.success(request, f"Товар «{product.name}» добавлен в корзину.")
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart['items']:
        del cart['items'][pid]
        cart['total_qty'] = sum(i['qty'] for i in cart['items'].values())
        cart['total_sum'] = sum(i['qty'] * i['price'] for i in cart['items'].values())
        _save_cart(request, cart)
        messages.info(request, "Товар удалён из корзины.")
    return redirect('cart_detail')

def cart_clear(request):
    request.session['cart'] = {'items': {}, 'total_qty': 0, 'total_sum': 0.0}
    request.session.modified = True
    messages.info(request, "Корзина очищена.")
    return redirect('cart_detail')

def cart_detail(request):
    cart = _get_cart(request)

    ids = [int(pid) for pid in cart['items'].keys()]
    products = Product.objects.filter(id__in=ids)

    id2slug = {p.id: p.slug for p in products}
    for pid, item in cart['items'].items():
        item['slug'] = id2slug.get(int(pid))
        item['subtotal'] = item['qty'] * item['price']
    return render(request, 'shop/cart.html', {'cart': cart})

def cart_checkout(request):
    cart = _get_cart(request)
    if cart['total_qty'] == 0:
        messages.warning(request, "Корзина пуста.")
        return redirect('product_list')

    request.session['cart'] = {'items': {}, 'total_qty': 0, 'total_sum': 0.0}
    request.session.modified = True
    messages.success(request, "Заказ оформлен! Спасибо за покупку.")
    return redirect('product_list')
