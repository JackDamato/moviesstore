from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, MovieRequest, MoviePetition
from django import forms
from django.contrib.auth.decorators import login_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
                      {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


class MovieRequestForm(forms.ModelForm):
    class Meta:
        model = MovieRequest
        fields = ["name", "description"]

@login_required
def requests_index(request):
    template_data = {}
    if request.method == "POST":
        form = MovieRequestForm(request.POST)
        if form.is_valid():
            movie_request = form.save(commit=False)
            movie_request.user = request.user
            movie_request.save()
            return redirect("movies.requests_index")
    else:
        form = MovieRequestForm()

    user_requests = MovieRequest.objects.filter(user=request.user).order_by("-date")
    template_data["form"] = form
    template_data["requests"] = user_requests
    return render(request, "movies/requests.html", {"template_data": template_data})

@login_required
def delete_request(request, id):
    movie_request = get_object_or_404(MovieRequest, id=id, user=request.user)
    movie_request.delete()
    return redirect("movies.requests_index")


class MoviePetitionForm(forms.ModelForm):
    class Meta:
        model = MoviePetition
        fields = ["movie_name", "petition_description"]


@login_required
def view_petitions(request):
    # display the petition page with all petitions and petition form
    template_data = {}
    if request.method == "POST":
        form = MoviePetitionForm(request.POST)
        if form.is_valid():
            movie_petition = form.save(commit=False)
            movie_petition.requested_by = request.user
            movie_petition.save()
        else:
            form = MoviePetitionForm()

    petitions = MoviePetition.objects.all().order_by("-votes")
    template_data["petitions"] = petitions
    template_data["form"] = MoviePetitionForm()
    return render(request, "movies/petitions.html", {"template_data": template_data})


@login_required
def approve_petition(request, id):
    petition = get_object_or_404(MoviePetition, id=id)
    if request.user in petition.voters.all():
        # user has already voted, do nothing
        return redirect("movies.view_petitions")
    petition.votes += 1
    petition.voters.add(request.user)
    petition.save()
    return redirect("movies.view_petitions")