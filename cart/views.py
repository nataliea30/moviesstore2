from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse 


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
    return render(request, 'cart/index.html', {'template_data': template_data})

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
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html', {'template_data': template_data})


# --- NEW FUNCTION FOR THE MAP DATA ---
def get_top_movies_by_state(request):
    """
    Calculates the top 3 most bought movies in each U.S. state.
    """
    # 1. Aggregate and order the data
    sales_aggregation = Item.objects.values(
        'order__state',
        'movie__name',
        'movie__id'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('order__state', '-total_quantity')

    
    # 2. Process the ordered list to extract only the top 3 per state
    top_movies_per_state = {}
    current_state = None
    rank = 0
    
    for sale in sales_aggregation:
        state = sale['order__state']
        
        # If we switch to a new state in the ordered list, reset the rank and list
        if state != current_state:
            current_state = state
            rank = 1
            top_movies_per_state[state] = []
        
        # Only include the top 3 for the current state
        if rank <= 3:
            top_movies_per_state[state].append({
                'rank': rank,
                'movie_id': sale['movie__id'],
                'movie_name': sale['movie__name'],
                'quantity': sale['total_quantity']
            })
            rank += 1
            
    # 3. Format the data into a list of objects for the frontend
    response_data = [
        {
            'state': state,
            'top_3_movies': movies
        }
        for state, movies in top_movies_per_state.items()
    ]
    
    # Return as a JSON response
    return JsonResponse(response_data, safe=False)