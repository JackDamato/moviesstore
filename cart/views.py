from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Order, Item, REGION_CHOICES


def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html',
        {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart.index')

    location = request.POST.get('location')
    if not location:
        messages.error(request, "You must select your region before purchasing!")
        return redirect('cart.index')

    movies_in_cart = Movie.objects.filter(id__in=cart.keys())
    cart_total = calculate_cart_total(cart, movies_in_cart)

    order = Order(user=request.user, total=cart_total)
    order.save()

    for movie in movies_in_cart:
        item = Item(
            movie=movie,
            price=movie.price,
            order=order,
            quantity=cart[str(movie.id)],
            location=location
        )
        item.save()

    request.session['cart'] = {}

    return render(request, 'cart/purchase.html', {'template_data': {'title': 'Purchase confirmation', 'order_id': order.id}})