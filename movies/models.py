from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')

    def __str__(self):
        return f"{self.id} - {self.name}"
    
    def purchase_stats(self):
        # Local import avoids circular import
        from cart.models import Item, REGION_CHOICES
        items = Item.objects.filter(movie=self)
        stats = {}
        for code, name in REGION_CHOICES:
            stats[name] = items.filter(location=code).count()
        return stats

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.movie.name}"

class MovieRequest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (by {self.user.username})"

class MoviePetition(models.Model):
    id = models.AutoField(primary_key=True)
    movie_name = models.CharField(max_length=255)
    petition_description = models.TextField()  # user description of why they want the movie
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)
    voters = models.ManyToManyField(User, related_name='voted_petitions', blank=True)
