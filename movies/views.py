from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Movie, Review, Rating

def index(request):
    movies = Movie.objects.all().order_by('name')
    template_data = {'title': 'Movies', 'movies': movies}
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = get_object_or_404(Movie, id=id)
    reviews = Review.objects.filter(movie=movie, parent__isnull=True).order_by('date')

    qs = Rating.objects.filter(movie=movie)
    rating_count = qs.count()
    avg = round(sum(r.value for r in qs) / rating_count, 2) if rating_count else 0

    user_rating = None
    if request.user.is_authenticated:
        ur = qs.filter(user=request.user).first()
        user_rating = ur.value if ur else None

    template_data = {
        'title': movie.name,
        'movie': movie,
        'reviews': reviews,
        'average_rating': avg,
        'rating_count': rating_count,
        'user_rating': user_rating,
    }
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST.get('comment', '') != '':
        movie = get_object_or_404(Movie, id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.parent = None
        review.save()
    return redirect('movies.show', id=id)

@login_required
def create_reply(request, id, review_id):
    if request.method == 'POST' and request.POST.get('comment', '') != '':
        parent = get_object_or_404(Review, id=review_id)
        if parent.movie_id != id:
            return redirect('movies.show', id=id)
        reply = Review()
        reply.comment = request.POST['comment']
        reply.movie = parent.movie
        reply.user = request.user
        reply.parent = parent
        reply.save()
    return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {'title': 'Edit Review', 'review': review}
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST.get('comment', '') != '':
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def popularity_map(request):
    return render(request, "movies/popularity_map.html", {"region_data": {}})

@login_required
def rate(request, id):
    if request.method != "POST":
        return redirect('movies.show', id=id)

    movie = get_object_or_404(Movie, id=id)

    # Validate the rating 1..5
    try:
        value = int((request.POST.get("rating") or "").strip())
    except Exception:
        value = None
    if value is None or value < 1 or value > 5:
        return redirect('movies.show', id=id)

    # Upsert per (movie, user)
    Rating.objects.update_or_create(
        movie=movie,
        user=request.user,
        defaults={'value': value}
    )

    # Redirect back so the page re-renders with updated averages
    return redirect('movies.show', id=id)